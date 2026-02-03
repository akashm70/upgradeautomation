# from netmiko import ConnectHandler 

# device = {
#             "device_type": "juniper", 
#             "host": "10.80.71.55", 
#             "username": "lab", 
#             "password": "lab123",
#         }
# c=ConnectHandler(**device)
# t=c.send_command("show version")
# print(t)
# c.disconnect()
import logging 
from netmiko import ConnectHandler 
from netmiko.exceptions import (
    NetmikoTimeoutException,
    NetmikoAuthenticationException
)
from paramiko.ssh_exception import SSHException
import sys
import time
import os
import yaml
import json 
def temp(device):
    conn = None

    host = device.get("devices")[0].get("host")
    device_type = device.get("devices")[0].get('device_type')
    vendor = device.get("devices")[0].get('vendor')
    min_disk_gb = device.get("devices")[0].get('min_disk_gb')

    print("Host:", host)
    print("Device Type:", device_type)
    print("Vendor:", vendor)
    print("Min Disk (GB):", min_disk_gb)

def load_yaml(filename): 
    """
    Docstring for load_yaml
    
    :param file_path: Description
    """
    try:
        curr_dir = os.getcwd()
        file_path = os.path.join(curr_dir, "inputs", filename)
        with open(file_path, "r") as f: 
            return yaml.safe_load(f)
    except Exception as e: 
        logger.error(f"Failed to load YAML {filename}: {e}")
        raise

d = load_yaml("deviceDetails.yaml")
print(d,type(d))

temp(d)
