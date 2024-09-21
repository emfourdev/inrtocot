import yaml
import sys


class Config:
    _instance = None

    def __new__(cls, config_file="config.yml"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            with open(config_file) as stream:
                try:
                    if sys.version_info.major < 3:
                        cls._instance.config = yaml.load(stream)
                    else:
                        cls._instance.config = yaml.load(stream, Loader=yaml.FullLoader)
                except yaml.YAMLError as e:
                    print(f"Error loading configuration: {e}")
                    exit(1)
        return cls._instance

    def get(self):
        return self.config


class AppConfig:
    def __init__(self, config):
        """Initialize with configuration dictionary."""

        # Configure TAK Server
        self.tak_config = config.get("tak_connection", {})
        self.tak_host = self.tak_config.get("host")
        self.tak_tls = self.tak_config.get("tls")
        self.tak_udp = self.tak_config.get("udp")
        self.tak_https = self.tak_config.get("https")
        self.tak_type = self.tak_config.get("type")
        self.no_tls_verify = self.tak_config.get("no_tls_verify")
        self.cert_p12 = self.tak_config.get("cert_p12")
        self.cert_pem = self.tak_config.get("cert_pem")
        self.cert_key = self.tak_config.get("cert_key")
        self.password = self.tak_config.get("password")

        self.garmin_config = config.get("garmin_connection", {})
        self.garmin_url = self.garmin_config.get("feed_url")
        self.g_username = self.garmin_config.get("g_username")
        self.g_password = self.garmin_config.get("g_password")
        self.cot_type = self.garmin_config.get("cot_type")
        self.cot_stale_time = self.garmin_config.get("cot_stale_time")


    def __getitem__(self, key):
        return getattr(self, key)

    def update_config(self, config):
        """Update configuration settings."""
        # Configure TAK Server
        self.tak_config = config.get("tak_connection", {})
        self.tak_host = self.tak_config.get("host")
        self.tak_tls = self.tak_config.get("tls")
        self.tak_udp = self.tak_config.get("udp")
        self.tak_https = self.tak_config.get("https")
        self.tak_type = self.tak_config.get("type")
        self.no_tls_verify = self.tak_config.get("no_tls_verify")
        self.cert_p12 = self.tak_config.get("cert_p12")
        self.cert_pem = self.tak_config.get("cert_pem")
        self.cert_key = self.tak_config.get("cert_key")
        self.password = self.tak_config.get("password")

        self.garmin_config = config.get("garmin_connection", {})
        self.garmin_url = self.garmin_config.get("url")
        self.garmin_password = self.garmin_config.get("password")
        self.cot_type = self.garmin_config.get("cot_type")
        self.cot_stale_time = self.garmin_config.get("cot_stale_time")
