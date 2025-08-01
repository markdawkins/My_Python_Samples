import os
import time
import ftplib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
SOURCE_FOLDER = "/home/mark/Downloads/qbitdownloads"  # Your source folder
FTP_SERVER = "192.168.1.142"
FTP_FOLDER = "/media/mark/vids3"  # Specific folder on FTP server
FTP_USER = "anonymous"
FTP_PASSWORD = "password"
CHECK_INTERVAL = 300  # 5 minutes in seconds
CHUNK_SIZE = 8192  # 8KB chunks for large files
MAX_RETRIES = 3  # Number of retries for failed uploads
RETRY_DELAY = 10  # Seconds to wait between retries

class FTPUploader:
    def __init__(self):
        self.ftp = None
        self.connect()
        
    def connect(self):
        try:
            if self.ftp is not None:
                try:
                    self.ftp.quit()
                except:
                    pass
            self.ftp = ftplib.FTP(FTP_SERVER, timeout=30)
            self.ftp.login(FTP_USER, FTP_PASSWORD)
            # Set passive mode (important for some networks)
            self.ftp.set_pasv(True)
            
            # Change to the specific folder, create if it doesn't exist
            self._ensure_ftp_folder()
            
            return True
        except Exception as e:
            print(f"FTP connection error: {e}")
            return False
    
    def _ensure_ftp_folder(self):
        """Ensure the target FTP folder exists and change to it"""
        try:
            self.ftp.cwd(FTP_FOLDER)
        except ftplib.error_perm:
            # Folder doesn't exist, try to create it
            try:
                self._create_ftp_path(FTP_FOLDER)
                self.ftp.cwd(FTP_FOLDER)
            except Exception as e:
                print(f"Could not create FTP folder {FTP_FOLDER}: {e}")
                raise
    
    def _create_ftp_path(self, path):
        """Create the full path on the FTP server"""
        path_parts = path.split('/')
        current_path = ""
        
        for part in path_parts:
            if not part:
                continue
            current_path += f"/{part}"
            try:
                self.ftp.cwd(current_path)
            except ftplib.error_perm:
                try:
                    self.ftp.mkd(current_path)
                    print(f"Created FTP directory: {current_path}")
                except Exception as e:
                    print(f"Error creating directory {current_path}: {e}")
                    raise
        
    def upload_file(self, file_path):
        retries = 0
        file_name = os.path.basename(file_path)
        
        while retries < MAX_RETRIES:
            try:
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    return False
                
                file_size = os.path.getsize(file_path)
                print(f"Attempting to upload {file_name} ({file_size/1024/1024:.2f} MB) to {FTP_FOLDER}...")
                
                # Reconnect if needed
                if not self.ftp:
                    if not self.connect():
                        time.sleep(RETRY_DELAY)
                        retries += 1
                        continue
                
                # Ensure we're in the correct folder
                self.ftp.cwd(FTP_FOLDER)
                
                with open(file_path, 'rb') as file:
                    # Use storbinary with chunks for large files
                    self.ftp.storbinary(f'STOR {file_name}', file, blocksize=CHUNK_SIZE)
                
                print(f"Successfully uploaded {file_name} to {FTP_FOLDER}")
                return True
                
            except ftplib.error_temp as e:
                print(f"Temporary FTP error uploading {file_name}: {e}")
                retries += 1
                if retries < MAX_RETRIES:
                    print(f"Retrying in {RETRY_DELAY} seconds... (attempt {retries + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY)
                    self.connect()  # Reconnect before retry
                continue
                
            except (ftplib.all_errors, IOError) as e:
                print(f"Error uploading {file_name}: {e}")
                return False
                
        print(f"Failed to upload {file_name} after {MAX_RETRIES} attempts")
        return False
        
    def close(self):
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                pass
            self.ftp = None

class FolderMonitor(FileSystemEventHandler):
    def __init__(self, uploader):
        self.uploader = uploader
        self.uploaded_files = set()
        
    def on_created(self, event):
        if not event.is_directory:
            self.process_file(event.src_path)
            
    def process_file(self, file_path):
        if os.path.exists(file_path) and file_path not in self.uploaded_files:
            try:
                # Wait a moment to ensure file is completely written
                time.sleep(5)
                
                # Check file size stability (for ongoing downloads)
                size1 = os.path.getsize(file_path)
                time.sleep(2)
                size2 = os.path.getsize(file_path)
                
                if size1 == size2:  # File isn't changing
                    if self.uploader.upload_file(file_path):
                        self.uploaded_files.add(file_path)
                else:
                    print(f"File {os.path.basename(file_path)} is still being modified, will retry later")
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

def check_existing_files(uploader, folder, monitor):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path) and file_path not in monitor.uploaded_files:
            monitor.process_file(file_path)

def main():
    uploader = FTPUploader()
    monitor = FolderMonitor(uploader)
    observer = Observer()
    
    try:
        # Set up watchdog to monitor for new files
        observer.schedule(monitor, SOURCE_FOLDER, recursive=False)
        observer.start()
        
        print(f"Monitoring {SOURCE_FOLDER} for new files...")
        print(f"Uploading to FTP server: {FTP_SERVER}{FTP_FOLDER}")
        while True:
            print("Performing periodic folder check...")
            check_existing_files(uploader, SOURCE_FOLDER, monitor)
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        observer.stop()
        observer.join()
        uploader.close()
        print("Cleanup complete. Exiting.")

if __name__ == "__main__":
    main()
