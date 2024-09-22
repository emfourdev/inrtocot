# Simple Inreach to CoT Gateway

## Overview

This is a simple Gateway that pulls the KML Feed from a Garmin Explorer Mapshare account, converts it to Cursor on Target (CoT), and then sends it to a TAK Server. It leverages the PyTAK library to create the CoT Packets and the transmission to the TAK Server. 

It can utilise either TLS, TCP, or UDP for transmissions and accepts all the common configuration options available to PyTAK. 

It was created as a gap filler as the excellent In Reach To CoT Gateway developed by snstac, https://github.com/snstac/inrcot, no longer appears to be maintained and I was unable to get it to successfully pull the feed from a mapshare account. 

## How to Use

- Clone the repository to a machine with access to your TAK Server. 
- Create a client certificate and private key pair if you are using TLS
- Configure the **config.yml** file
- Run the script using **python main.py**
- If you want to run it in the background you can either use a tool like **screen** or simply use **python main.py &**
  
## Configuration File
  - **host:** Change to either the FQDN or IP Address of your TAK Server
  - **tls:** If you are using TLS then change to the port of the connector configured on your TAK Server
  - **udp:** If you are not using an encrypted connection then change this to the port of your plain text connector
  - **type:** Select whether you are using TLS/UDP/TCP
  - **no_tls_verify:** If you are using self-signed certificates and have not installed your CA onto the machine enable this option to tell PyTAK to ignore any Certificate Verification Errors.
  - **cert_pem:** This is the location of the client certificate you created for the application in PEM format
  - **cert_key:** The accompanying private key is also in PEM format
  - **password:** If you set a password for your client certificate. Enter it here. 
  - **feed_url:** Obtain the Feed URL from your Mapshare account. This can be found in the social section. Use the RAW Feed URL.
  - **g_username and g_password:** If you have authentication setup for your feed then enter the Password that you set (you can only set a password) for both the username and password.
  - **cot_type:** Change the type to whatever you want. An explanation of CoT Types can be found here https://freetakteam.github.io/FreeTAKServer-User-Docs/About/architecture/mil_std_2525/#level-4-function-code
  - **cot_stale_time:** This is how long the tracker will appear on your display before it times out. If the device is active then this will be constantly updated. Once it goes offline then it will stale out and disappear after this time

## Requirements

- Python 3.8 or Newer
- PyYAML~=6.0.1
- aiohttp~=3.10.5
- pytak~=7.1.0
- fastkml~=0.12
<<<<<<< HEAD
- lxml~=5.3.0
=======
- lxml~=5.3.0
>>>>>>> inrtocot/main
