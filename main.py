import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from prechecks import PreCheck
from lib.utilities import *
from parsers.junos.junos_mx80 import * 

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s %(levelname)s %(name)s %(message)s"
# )

MAX_THREADS = 5

# Setup logger FIRST
# log_file = setup_logger(
#     vendor=device["vendor"],
#     model="mx480"
# )

# ----------------------------------------------------
# Worker Function (Runs per device)
# ----------------------------------------------------
def run_prechecks(device):
    print("Running Prechecks..")
    host = device.get("devices")[0].get("host")
    model = device.get("devices")[0].get("model")
    device_type = device.get("devices")[0].get('device_type')
    username = device.get("devices")[0].get("username")
    password = device.get("devices")[0].get("password")
    start_time = datetime.now()
    logger = setup_logger(device_type, model)
    logger.info(f"{host} — Prechecks started at {start_time}")
    PRE_CHECK_TIMESTAMP = datetime_conversion(start_time)

    precheck = PreCheck(device)

    print(f" device details: \n host: {host}")

    try:
        # Step 1 — Version
         version_ouput=precheck.showVersion(device_type, logger)
         #print(f" version output: {version_output}")
        # Step 2 — Backup Config
        # runConfig = precheck.runningConfig(f"junos_running.conf", "EFFPER01")
        # print(f" running config: {runConfig}")
        # logger.info(f"Running config: {runConfig}")
        
        # commands=load_yaml("show_cmd_list.yaml")
        # print(f"commands: {commands}")
        # print("Executing commands")
        # execute_command(commands,device_type, host, username,password,model)
        # print(f"command_output: {COMMAND_OUTPUT_STORE.get("show arp no-resolve | no-more")}")
        
        # Parsing the data 
        # output = parse_show_arp_no_resolve()

        # print(f" Parse data: {output}")
        # # # Step 2b — Backup Logs
        # precheck.deviceLog(f"{device_type}_{PRE_CHECK_TIMESTAMP}_logs", "EFFPER01")

        # # Step 3 — Storage Check (5GB threshold)
        # result = precheck.checkStorage()
        # logger.info(f"{host} — Storage Result: {result}")

        # # Step 4 — Disable Filter
        #precheck.disableFilter()
        # #call the parser(->json)
    
    except Exception as e:
        logger.error(f"{host} — Precheck failed: {e}")

    finally:
        precheck.disconnect()
        end_time = datetime.now()
        logger.info(f"{host} — Prechecks completed at {end_time}")


# ----------------------------------------------------
# Main Function
# ----------------------------------------------------
def main():
    devices = load_yaml("deviceDetails.yaml")
    print(f" device: {devices}")

#change this to choose the device 
        # setup logger ONC
    # devic/e_details: 
    run_prechecks(devices)
    # with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    #     futures = [
    #         executor.submit(run_prechecks, devices)
    #         for device in devices["devices"]
            
    #     ]

    #     print(f" futures: {futures}")

    #     for future in as_completed(futures):
    #         try:
    #             future.result()
    #         except Exception as e:
    #             logger.error(f"Thread execution error: {e}")


if __name__ == "__main__":
    main()
#store the ouput in a text file 

