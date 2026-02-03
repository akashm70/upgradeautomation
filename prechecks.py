import logging 
from netmiko import ConnectHandler 
from lib.utilities import * 

# logger = logging.getLogger(__name__)
#----------------------------------------------------#
# PreCheck class
#----------------------------------------------------#
class PreCheck: 

    """
    Handles configuration and log backups from devices. 
    Currently support JUNOS devices

    """

    def __init__(self, device): 
         self.device = device
         self.conn = None 
         self.host = device.get("devices")[0].get("host")
         self.device_type = device.get("devices")[0].get('device_type')
         self.vendor = device.get("devices")[0].get('vendor')
         self.model = device.get("devices")[0].get('model')
         self.min_disk_gb = device.get("devices")[0].get('min_disk_gb')
         
        #  self.logger = setup_logger(__name__)


    # -------------------------------
    # Connection Handling 
    # -------------------------------
    def connect(self):
         logger.info(f"Connecting to {self.host}")
         print("type of device", self.device.get("devices")[0].get('device_type'))
         session_log_dir = os.path.join(os.getcwd(), "outputs")
         os.makedirs(session_log_dir, exist_ok=True)

         session_logs_file = f"{self.vendor}_{self.model}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
         session_logs_path = os.path.join(session_log_dir, session_logs_file)

         if not self.conn:
            self.conn = login_device(
                device_type = self.device.get("devices")[0].get('device_type'),
                host = self.device.get("devices")[0].get("host"),
                username = self.device.get("devices")[0].get("username"), 
                password = self.device.get("devices")[0].get("password"),
                session_log_path= session_logs_path
            )
            # print(conn)

    def disconnect(self): 
         if self.conn: 
              logout_device(self.conn, self.device.get("devices")[0].get("host"))
              self.conn = None 

    def showVersion(self, device_type, logger):
        """
        Detect vendor and execute show version for specific model
        to get current OS version and firmware version
        """
        try:
            print("Running show version")
            conn = self.connect()
            logger.info("Connected to device")
            print(f" Device type: {device_type}")
            if not self.conn:
                print("Not connected to device")
                logger.error("Not connected to device")
                raise RuntimeError("Not connected to device")
            
            if (
                self.vendor not in  ["juniper", "cisco"]
            ):
                logger.error(f"Unsupported vendor: {self.device_type}")
                raise ValueError(f"Unsupported vendor: {self.device_type}")

            command = "show version"
            print(f"{command}")
            logger.info(f"{self.host}: Executing '{command}'")
            output = self.conn.send_command(command)
            print("\nOP START\n", output, "\nOP END\n")

            COMMAND_OUTPUT_STORE[command] = {
                "device": self.host, 
                "output": output
            }

            logger.info(f"{self.host}: Version information retrieved")
            
            return output

        except Exception as e:
            logger.error(f"{self.host}: Show version failed: {e}")
            self.disconnect()
            raise
        # finally:
        #     self.disconnect()

    # -------------------------------
    # Backup Running Config 
    # -------------------------------
    def runningConfig(self, filename, device_name):
        """
        Backup Running configuration to local file
        """
        
        try: 
            if not self.conn:
                logger.error("Not connected to device")
                raise RuntimeError("Not connected to device")
                exit
            
            if (
                "juniper" not in self.device_type
                and "cisco" not in self.device_type
            ):
                logger.error(f"Unsupported vendor: {self.device_type}")
                raise ValueError(f"Unsupported vendor: {self.device_type}")
            
            if self.vendor == "juniper":
                commands = [
                    "configure private",
                    f"save {filename}",
                    "run file list", 
                    f"scp {device_name}:/tmp/{filename} ./"
                ]

            output = ""
            for cmd in commands:
                logger.info(f"{self.host}: Excecuting '{cmd}'")
                output += self.conn.send_command(cmd) + "\n"

            with open(filename, "w") as f:
                f.write(output)

            logger.info(f"{self.host}: Running config saved to {filename}")
            return output

        except Exception as e:
            logger.error(f"{self.host}: Running config Backup failed: {e}")
            raise
    
    # -------------------------------
    # Backup Device logs 
    # -------------------------------
    def deviceLog(self, filename, device_name): 
        """
        Archive and backup device logs
        """
        
        try:
            conn = self.connect()
            if not self.conn: 
                logger.error("Not connected to device")
                raise RuntimeError("Not connected to device")
                exit
        
          
            if self.vendor == "juniper":
            
                commands = [
                    f"request support information | save /var/log/{filename}.txt \n", 
                    f"file archive compress source /var/log/* destination /var/tmp/{filename}.tar.gz\n"
                    f"scp {device_name}:/var/tmp/{filename}.txt ./ \n"
                ]
            output = ""
            for cmd in commands:
                logger.info(f"{self.host}: Excecuting '{cmd}'")
                output += self.conn.send_command_timing(cmd) + "\n"
                print(f" output: {output}")


            with open(filename, "w") as f:
                f.write(output)
                
            logger.info(f"{self.host}: Device logs archived to {filename}")
        except Exception as e: 
            logger.error(f"{self.host}: Device log backup failed: {e}")
            raise
            
    
    # -------------------------------
    # Backup disk1 config to disk2 
    # -------------------------------
    def copyBackup(self): 
        """
        Check number of disks on a Junos device
        Backing up the whole primary disk1 config to disk2 for rollback
        """
        try: 
            if not self.conn: 
                logger.error("Not connected to device")
                raise RuntimeError("Not connected to device")
            
            if (
                "junos" not in self.vendor.lower()
                or "cisco" not in self.vendor.lower()
            ): 
                logger.error(f"Unsupported vendor: {self.vendor}")
                raise ValueError(f"Unsupported vendor: {self.vendor}")

            if self.vendor.lower() == "junos": 
                command = "show chassis hardware | match Drive"
                output = self.conn.send_command(command)

                disk_info = {
                    "set-b": [], 
                    "set-p": []
                }

                if not output.strip(): 
                    return disk_info 
                
                for line in output.splitlines(): 
                    line_lower = line.lower() 

                    if "set-b" in line_lower: 
                        disk_info["set-b"].append(line.strip())
                    
                    if "set-p" in line_lower: 
                        disk_info["set-p"].append(line.strip())
                total_disks = len(disk_info["set-b"]) + len(disk_info['set-p'])
                if total_disks > 1:
                    cmd = "request vmhost snapshot"
                    output += self.conn.send_command(cmd)
                    logger.info(f"{self.host}: Excecuting '{cmd}'")
                    logger.debug(f"copybackup\n: {output}")
                    logger.info(f"{self.host}: Disk1 backup is done")
                
                return output
        except Exception as e: 
            logger.error(f"{self.host}: Disk backup failed: {e}")
            raise
    # -------------------------------
    # Step 3: Check Storage & Cleanup
    # -------------------------------
    def checkStorage(self):

        try:
            conn=self.connect()
            if not self.conn:
                logger.error("Not connected to device")
                raise RuntimeError("Not connected to device")
            
            # if (
            #     "junos" not in self.vendor.lower()
            #     and "cisco" not in self.vendor.lower()
            # ):
            #     logger.error(f"Unsupported vendor: {self.vendor}")
            #     raise ValueError(f"Unsupported vendor: {self.vendor}")
            

            logger.info(f"{self.host}: Checking system storage")
 
            storage_output = self.conn.send_command("show system storage")
            mount = "/var"
            free_gb = None
 
            # Parse storage
            for line in storage_output.splitlines():
                if mount in line:
                    parts = line.split()
                    avail = parts[3]
                    if avail.endswith("G"):
                        free_gb = float(avail[:-1])
                    elif avail.endswith("M"):
                        free_gb = float(avail[:-1]) / 1024
 
            if free_gb == None:
                raise ValueError("Unable to parse storage output")
 
            logger.info(f"{self.host}: Free space {free_gb} GB")
 
            # Enough space
            if free_gb >= self.min_disk_gb:
                return {"status": "OK", "free_gb": free_gb}
 
            # ---------------------------------------------------
            # LOW STORAGE → START CLEANUP
            # ---------------------------------------------------
            logger.warning(f"{self.host}: Low space! Running system cleanup")
 
            # No yes/no handling — direct execution
            cleanup_output = self.conn.send_command(
                "request system storage cleanup"
            )
 
            # ---------------------------------------------------
            # Delete files from YAML
            # ---------------------------------------------------
            files_to_delete = self.device.get("cleanup_files", [])
 
            if not files_to_delete:
                logger.warning(
                    f"{self.host}: cleanup_files EMPTY → Deleting ALL temp files!"
                )
                delete_out = self.conn.send_command(
                    "file delete /var/tmp/*"                )
                return {
                    "status": "ALL_FILES_DELETED",
                    "free_gb_before": free_gb,
                    "cleanup_output": cleanup_output,
                    "delete_output": delete_out
                }
 
            delete_results = []
            for file in files_to_delete:
                logger.info(f"{self.host}: Deleting {file}")
                out = self.conn.send_command(f"file delete {file}", expect_string=r"#")
                delete_results.append({file: out})
 
            return {
                "status": "SELECTED_FILES_DELETED",
                "free_gb_before": free_gb,
                "cleanup_output": cleanup_output,
                "deleted_files": delete_results
            }
 
        except Exception:
            logger.exception(f"{self.host}: Storage cleanup failed")
            raise
       
    def disableReProtectFilter(self):
        """
        Removes RE protection firewall filter from loopback interface (lo0).
         show configuration | display set | match lo0.0
        set interfaces lo0 unit 0 family inet filter input PROTECT-RE-FILTER
        """
        try:
            if not self.conn: 
                logger.error("Not connected to device")
                raise RuntimeError("Not connected to device")
                exit

            if (
                "junos" not in self.vendor.lower()
                or "cisco" not in self.vendor.lower()
            ): 
                logger.error(f"Unsupported vendor: {self.vendor}")
                raise ValueError(f"Unsupported vendor: {self.vendor}")
            
            if self.device_type== "juniper":
                logger.error("RE Protect filter disable supported only for Junos")
                raise ValueError("RE Protect filter disable supported only for Junos")

            commands = [
                "delete interfaces lo0 unit 0 family inet filter input",
                "delete interfaces lo0 unit 0 family inet6 filter input",
                "commit"
            ]

            output = ""
            for cmd in commands:
                logger.info(f"{self.host}: Executing '{cmd}'")
                output += self.conn.send_command(cmd) + "\n"

            return output

        except Exception:
            logger.exception(f"{self.host}: Disable RE protect filter failed")
            raise


