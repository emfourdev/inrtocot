import asyncio
import aiohttp
import pytak
from fastkml import kml
from lxml import etree
from datetime import datetime
from datetime import timedelta
import socket
import logging
from configparser import ConfigParser
from config.config import Config
from config.config import AppConfig

config = Config().get()
app_config = AppConfig(config)


class MySender(pytak.QueueWorker):
    """
    Defines how you process or generate your Cursor-On-Target Events.
    From there it adds the COT Events to a queue for TX to a COT_URL.
    """

    async def handle_data(self, data):
        """Handle pre-CoT data, serialize to CoT Event, then puts on queue."""
        event = data
        await self.put_queue(event)

    async def run(self, number_of_iterations=-1):
        """Run the loop for processing or generating pre-CoT data."""
        while 1:

            # Fetch Garmin KML feed
            kml_data = await fetch_kml_feed(app_config.garmin_url, app_config.g_username, app_config.g_password)
            if kml_data is None:
                return

            # Parse KML feed into placemarks
            placemarks = parse_kml(kml_data)
            if not placemarks:
                logging.error("No placemarks found in KML feed.")
                return

            data = create_cot_event(placemarks)
            for event in data:
                logging.info("Sending:\n%s\n", event.decode())
                await self.handle_data(event)
                await asyncio.sleep(120)


async def fetch_kml_feed(url, username, password):
    auth = aiohttp.BasicAuth(username, password)
    async with aiohttp.ClientSession(auth=auth) as session:
        async with session.get(url) as response:
            if response.status == 200:
                logging.info(f"KML Feed Successfully Fetched")
                return await response.text()
            else:
                logging.error(f"Error fetching KML feed: {response.status}")
                return None


def parse_kml(kml_data):
    k = kml.KML()
    k.from_string(kml_data.encode())

    ns = "{http://www.opengis.net/kml/2.2}"  # KML namespace

    placemarks = []
    # Parse through the KML to find placemarks
    for document in k.features():
        for folder in document.features():
            for placemark in folder.features():
                if isinstance(placemark, kml.Placemark):
                    coords = placemark.geometry.coords[0]
                    name = placemark.name
                    placemarks.append(
                        {
                            "name": name,
                            "lat": coords[1],
                            "lon": coords[0],
                            "description": (
                                placemark.description
                                if placemark.description
                                else "No description"
                            ),
                        }
                    )
    return placemarks


def create_cot_event(placemarks):
    """Create a Cursor-on-Target (CoT) message from a KML placemark."""
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    stale = (datetime.utcnow() + timedelta(seconds=app_config.cot_stale_time)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    cot_events = []  # List t
    # o hold multiple CoT events
    for placemark in placemarks:
        cot_event = etree.Element("event")
        cot_event.set("version", "2.0")
        cot_event.set("uid", f"Garmin-{placemark['name']}")
        cot_event.set("time", now)
        cot_event.set("start", now)
        cot_event.set("stale", stale)
        cot_event.set("type", app_config.cot_type)
        cot_event.set("how", "m-g")

        point = etree.SubElement(cot_event, "point")
        point.set("lat", str(placemark["lat"]))
        point.set("lon", str(placemark["lon"]))
        point.set("ce", "9999999.0")  # Circular Error
        point.set("le", "9999999.0")  # Linear Error
        point.set("hae", "0")  # Height Above Ellipsoid

        detail = etree.SubElement(cot_event, "detail")
        contact = etree.SubElement(detail, "contact")
        contact.set("callsign", placemark["name"])

        remarks = etree.SubElement(detail, "remarks")
        remarks.set("value", placemark["description"])

        #return etree.tostring(cot_event, pretty_print=True)
        cot_events.append(etree.tostring(cot_event, pretty_print=True))
    return cot_events


async def main():

    logging.basicConfig(
        level=logging.INFO,
        filename="inrtocot.log",
        filemode="w",
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # Import the configuration from the Config File


    # Check that the TAK Server is configured in the configuration file
    if app_config.tak_host is None:
        print(
            "Missing TAK Server address in config (host:<address> in connection section)"
        )
        logging.error("Missing TAK Server address", exc_info=True)
        exit(1)

    # Determine whether we are using TLS or UDP
    if app_config.tak_type == "tls":
        tak_port = app_config.tak_tls
    else:
        tak_port = app_config.tak_udp

    # Check that TAK Server is responding
    print("Check Connectivity")
    print("==================")
    taksock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Check that we can communicate with the TAK Server
    if taksock.connect_ex((app_config.tak_host, tak_port)) == 0:
        print("TAK Server Online: OK")
        logging.info(f"TAK Server is Online")
        logging.info(f"TAK Host: {app_config.tak_host} Port: {tak_port}")

        # Configure Streaming Connection to TAK Server
        pytak_config = ConfigParser()
        pytak_host = "tls://{tak_host}:{tak_port}".format(
            tak_host=app_config.tak_host, tak_port=tak_port
        )
        pytak_config["mycottool"] = {
            "COT_URL": pytak_host,
            "PYTAK_TLS_CLIENT_CERT": app_config.cert_pem,
            "PYTAK_TLS_CLIENT_KEY": app_config.cert_key,
            "PYTAK_TLS_DONT_VERIFY": app_config.no_tls_verify,
        }

        pytak_config = pytak_config["mycottool"]
    else:
        print("TAK Server Online: FAILED")
        logging.error(f"TAK Server is Offline")
        logging.error(f"TAK Host: {app_config.tak_host} Port: {tak_port}")
        print("Exiting...")
        exit(1)

    taksock.close()

    # Initializes worker queues and tasks.
    cot_url = pytak.CLITool(pytak_config)
    await cot_url.setup()

    # Add your serializer to the asyncio task list.
    cot_url.add_tasks(set([MySender(cot_url.tx_queue, pytak_config)]))

    # Start all tasks and exit after sending the packets.
    await cot_url.run()

if __name__ == "__main__":
    asyncio.run(main())
