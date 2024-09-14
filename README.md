# SNI-Checker
Easy filter domains that support TLS 1.3 and HTTP/2.

**DONT RUN ON THE SERVER**

## Install
To install checker run the following command:
```
bash -c "$(wget -qO- https://raw.githubusercontent.com/jomertix/SNI-Checker/main/run.sh)" && cd SNI-Checker
```

## Usage 
1. Open https://bgp.tools
2. Enter the IP of your server
3. Open the "DNS" tab and select "Show Forward DNS"
4. Copy all the domains with their ips

Create a file and paste copied domains into it. Now run the script
```
python3 main.py
```
and enter the path - relative or absolute - to the file with the copied domains. After program completion, domains that supports TLS 1.3 and H2 will be saved in "verified_domains.txt", domains with ping are in "verified_domains_with_ping.txt"
