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
from datetime import datetime

LOG_DIR = os.path.join(os.getcwd(), "logging")
os.makedirs(LOG_DIR, exist_ok=True)
"""
Global store for device command outputs
"""
COMMAND_OUTPUT_STORE = {} 
PRE_CHECK_TIMESTAMP = "" 
VENDOR = ""
MODEL = ""
VERSION = ""
# logger = None


logging.basicConfig(
    level = logging.INFO, 
    format= "%(asctime)s - %(levelname)s - %(message)s"
)
# logger = logging.getLogger(device_logs  )
logger = logging.getLogger(__name__)

#---------------------------------------------#
# Converting timestamp
#---------------------------------------------#

def datetime_conversion(timestamp):

    dt = datetime.strptime(f"{timestamp}", "%Y-%m-%d %H:%M:%S.%f")

    PRE_CHECK_TIMESTAMP = dt.strftime("%d%m%Y_%H%M%S") + f"{dt.microsecond // 1000:03d}"

    print(PRE_CHECK_TIMESTAMP)
    return PRE_CHECK_TIMESTAMP

#---------------------------------------------#
# Enable Logger functionality 
#---------------------------------------------#
def setup_logger(vendor, model):
    """
    Setup logger with VENDOR and MODEL specific log file
    """
    log_dir = os.path.join(os.getcwd(), "logging")
    os.makedirs(log_dir, exist_ok=True)

    log_file = f"{vendor}_{model}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger(f"{vendor}_{model}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    handler = logging.FileHandler(log_path)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d_%H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger

#---------------------------------------------#
# Writing the output into JSON file 
#---------------------------------------------#
def write_json(command_name,VENDOR, MODEL, json_data, json_file_path): 
    """
    Docstring for write_json
    
    :param command_name: Providing the command name
    :param json_data: Adding the command output 
    :return: Return the output JSON file along with timestamp
    """
    if not all([command_name, VENDOR, MODEL]): 
        logger.error("Command name, VENDOR, and MODEL cannot be empty")
        raise ValueError("Invalid Parameters")
    
    try:
        logger.info("Writing to JSON file ...")
        curr_dir = os.getcwd()
        output_dir = os.path.join(curr_dir, json_file_path)
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{VENDOR}_{MODEL}_{PRE_CHECK_TIMESTAMP}.json"
        print(f" Filname: {filename}")

        file_path = os.path.join(output_dir, filename)
        print(f" file path: {file_path}")

        if os.path.exists(file_path): 
            with open(file_path, "r") as f: 
                data = json.load(f)
        else:
            data = {
                "metadata": {
                    "timestamp": PRE_CHECK_TIMESTAMP, 
                    "vendor": VENDOR, 
                    "model": MODEL, 
                    "version": VERSION
                }, 
                "commands": {}
            }
        
        data["commands"][command_name] = json_data
        print(f" data: {data}")
        with open(file_path, "w") as f: 
            json.dump(data, f, indent=2)

        logger.info(f"JSON file written successfully: {file_path}")
        return data
    
    except FileNotFoundError as e: 
        logger.error(f"File error: {e}")
        raise
    except PermissionError as e: 
        logger.error(f"Permission denied while writing JSON: {e}")
        raise
    except json.JSONDecodeError as e: 
        logger.error(f" Invalid JSON format in existing file: {e}")
        raise
    except Exception as e: 
        logger.error(f"Unexpected error while writing JSON: {e}")
        raise


#---------------------------------------------#
# Login into device
#---------------------------------------------#
def login_device(host, username, password, device_type, session_log_path): 
    try: 
        logger.info(f"Connecting to {host} using Netmiko...") 

        device = {
            "device_type": device_type, 
            "host": host, 
            "username": username, 
            "password": password,
            "session_log": session_log_path
        }

        conn = ConnectHandler(**device)
        logger.info(f"Login Successful to {host}")
        
        return conn

    except NetmikoTimeoutException: 
        logger.error(f"{host}: Connection Timed out")
        raise
    except NetmikoAuthenticationException: 
        logger.error(f"{host}: Authentication Failed")
        raise
    except SSHException as e: 
        logger.error(f"{host}: SSH error: {e}")
        raise
    except Exception as e: 
        logger.error(f"{host}: Unknown error: {e}")
        raise

#---------------------------------------------#
# Logout from device
#---------------------------------------------#
def logout_device(conn, host): 
    try: 
        if conn:
            conn.disconnect()
            logger.info(f"Logout successful{f' from {host}' if host else ''}")
        else: 
            logger.warning("Logout skipped: connection object is None")
    except Exception as e: 
        logger.error(f"{host if host else 'Device'}: Logout failed: {e}")

#---------------------------------------------#
# Parsing the data
#---------------------------------------------#
# def parser()

#---------------------------------------------#
# YAML loader
#---------------------------------------------#
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

# run the execute command 
def execute_command(commands, device_type, host, username, password, MODEL):
    """
    Execute show commands from YAML and store output globally
    Always logout from device on error or success
    """
    conn = None
    output_file = f"{device_type}_{MODEL}_{PRE_CHECK_TIMESTAMP}.txt"
    try: 

        
        if device_type not in commands: 
            raise ValueError(f"No commands found for VENDOR: {device_type}")

        conn = login_device(
            device_type = device_type,
            host = host,
            username = username, 
            password = password,
        )

        for cmd in commands.get(device_type): 
            logger.info(f"{host}: Executing: '{cmd}'")
            try: 
                output = conn.send_command(cmd)
                COMMAND_OUTPUT_STORE[cmd] = {
                    "device": host, 
                    "output": output
                }
                # write to text file
                write_command_output_to_file(
                    output_file,
                    cmd,
                    COMMAND_OUTPUT_STORE[cmd]
                )
            except Exception as e: 
                logger.error(f"{host}: Command Failed: '{cmd}': {e}")
                COMMAND_OUTPUT_STORE[cmd] = {
                    "device": host, 
                    "error": str(e)
                }
                raise
                exit
        return COMMAND_OUTPUT_STORE
    except Exception as e: 
        logger.exception("Command execution Failed")
        raise 
        exit
    finally: 
        if conn: 
            logout_device(conn, host)


def write_command_output_to_file(filename, command, result):
    try:
        print("Writing the output to text file")
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, filename)

        with open(file_path, "a") as f:
            f.write(f"{command}\n")
            
            if "output" in result:
                f.write(result["output"] + "\n")
            else:
                f.write(f"ERROR: {result['error']}\n")

            
    except Exception as e:
        logger.error(
            f"{device}: Failed to write output from command '{command}' to file: {e}"
        )
        exit
