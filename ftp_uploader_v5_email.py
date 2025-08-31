import os
import time
import ftplib
import smtplib
import logging
from email.message import EmailMessage
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
SOURCE_FOLDER = "/home/mark/Downloads/qbitdownloads"
FTP_SERVER = "192.168.1.199"
FTP_FOLDER = "/mnt/mydisk/media/vids2"
FTP_USER = "" #username
FTP_PASSWORD = "" ##password
CHECK_INTERVAL = 300
CHUNK_SIZE = 65536
MAX_RETRIES = 5
RETRY_DELAY = 30
MIN_STABLE_TIME = 120
MAX_WAIT_TIME = 3600

# Email Configuration
EMAIL_SENDER = ""##"sender_email_eg_code.lab.072025@gmail.com"<<<<--- Change this >>>>
EMAIL_RECEIVER = "" ###user@gmail.com" <<<<--- Change this >>>>
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = ##"sender_email_eg_code.lab.072025@gmail.com"         <<<<--- Change this >>>>
SMTP_PASSWORD = ##"" "1965 6361 jkmb qdzu sulp euzc 2025"  # Use an App Password if 2FA is enabled <<<<--- Change this >>>>
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ftp_uploader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FTPUploader:
    def __init__(self):
        self.ftp = None
        self.connect()
        self.last_activity = time.time()
        
    def connect(self):
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                if self.ftp:
                    try:
                        self.ftp.quit()
                    except:
                        pass
                
                logger.info(f"Attempting FTP connection (attempt {attempt}/{max_retries})")
                self.ftp = ftplib.FTP(FTP_SERVER, timeout=120)
                self.ftp.login(FTP_USER, FTP_PASSWORD)
                self.ftp.set_pasv(True)
                self._ensure_ftp_folder()
                logger.info("FTP connection established successfully")
                return True
            except Exception as e:
                logger.error(f"FTP connection failed (attempt {attempt}): {e}")
                if attempt < max_retries:
                    time.sleep(RETRY_DELAY)
        return False
    
    def _ensure_ftp_folder(self):
        try:
            self.ftp.cwd(FTP_FOLDER)
        except ftplib.error_perm:
            try:
                self._create_remote_path(FTP_FOLDER)
                self.ftp.cwd(FTP_FOLDER)
            except Exception as e:
                logger.error(f"Failed to ensure FTP folder: {e}")
                raise
    
    def _create_remote_path(self, remote_path):
        path_parts = [p for p in remote_path.split('/') if p]
        current_path = ""
        
        for part in path_parts:
            current_path += f"/{part}"
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    if not self.ftp:
                        self.connect()
                    
                    try:
                        self.ftp.cwd(current_path)
                        break
                    except ftplib.error_perm:
                        self.ftp.mkd(current_path)
                        logger.info(f"Created remote directory: {current_path}")
                        break
                except (ftplib.error_temp, ConnectionError) as e:
                    logger.warning(f"Temporary error creating path (attempt {attempt}): {e}")
                    if attempt < max_retries:
                        time.sleep(RETRY_DELAY)
                        self.connect()
                    else:
                        raise
                except Exception as e:
                    logger.error(f"Error creating remote path: {e}")
                    raise
    
    def upload_file(self, file_path, relative_path=""):
        file_name = os.path.basename(file_path)
        self.last_activity = time.time()
        
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if not os.path.exists(file_path):
                    logger.warning(f"File not found: {file_path}")
                    return False
                
                logger.info(f"Attempt {attempt}/{MAX_RETRIES} for {file_name}")
                
                if not self.ftp and not self.connect():
                    time.sleep(RETRY_DELAY)
                    continue
                
                if relative_path:
                    try:
                        remote_path = os.path.join(FTP_FOLDER, relative_path)
                        self._create_remote_path(remote_path)
                    except Exception as e:
                        logger.error(f"Error creating remote directories: {e}")
                        continue
                
                file_size = os.path.getsize(file_path)
                logger.info(f"Uploading {file_name} ({file_size/1024/1024:.2f} MB)...")
                
                remote_full_path = os.path.join(FTP_FOLDER, relative_path, file_name) if relative_path else os.path.join(FTP_FOLDER, file_name)
                with open(file_path, 'rb') as f:
                    self.ftp.storbinary(f'STOR {remote_full_path}', f, blocksize=CHUNK_SIZE)
                
                logger.info(f"Successfully uploaded {remote_full_path}")
                return True
                
            except (ftplib.error_temp, ConnectionError) as e:
                logger.warning(f"Temporary error (attempt {attempt}): {e}")
                time.sleep(RETRY_DELAY)
                self.connect()
            except Exception as e:
                logger.error(f"Fatal error uploading {file_name}: {e}")
                break
                
        logger.error(f"Failed to upload {file_name} after {MAX_RETRIES} attempts")
        return False
    
    def is_file_stable(self, file_path):
        try:
            stat1 = os.stat(file_path)
            size1 = stat1.st_size
            mtime1 = stat1.st_mtime
            
            time.sleep(MIN_STABLE_TIME/2)
            stat2 = os.stat(file_path)
            
            return (size1 == stat2.st_size and 
                   mtime1 == stat2.st_mtime and
                   (time.time() - stat2.st_mtime) >= MIN_STABLE_TIME/2)
        except Exception as e:
            logger.warning(f"Error checking file stability: {e}")
            return False
        
    def close(self):
        if self.ftp:
            try:
                self.ftp.quit()
                logger.info("FTP connection closed properly")
            except Exception as e:
                logger.warning(f"Error closing FTP connection: {e}")

class FolderMonitor(FileSystemEventHandler):
    def __init__(self, uploader):  # Now properly accepts uploader argument
        super().__init__()
        self.uploader = uploader
        self.pending_items = {}
        self.last_check = time.time()
        
    def on_created(self, event):
        if not event.is_directory:
            self._handle_new_item(event.src_path, False)
        else:
            self._handle_new_item(event.src_path, True)
            
    def _handle_new_item(self, path, is_directory):
        if path not in self.pending_items:
            item_type = "directory" if is_directory else "file"
            logger.info(f"New {item_type} detected: {os.path.basename(path)}")
            self.pending_items[path] = {
                'first_seen': time.time(),
                'last_checked': 0,
                'stable': False,
                'is_directory': is_directory,
                'processed': False
            }
    
    def check_pending_items(self):
        current_time = time.time()
        if current_time - self.last_check < 60:
            return
            
        self.last_check = current_time
        logger.debug("Checking pending items...")
        
        for path, item_info in list(self.pending_items.items()):
            try:
                if item_info['processed']:
                    continue
                
                if not os.path.exists(path):
                    logger.warning(f"Item disappeared: {os.path.basename(path)}")
                    self.pending_items.pop(path)
                    continue
                
                if current_time - item_info['first_seen'] > MAX_WAIT_TIME:
                    logger.warning(f"Timeout waiting for item: {os.path.basename(path)}")
                    self.pending_items.pop(path)
                    continue
                
                if item_info['is_directory']:
                    self._process_directory(path)
                    item_info['processed'] = True
                    self.pending_items.pop(path)
                else:
                    if self.uploader.is_file_stable(path):
                        relative_path = os.path.relpath(os.path.dirname(path), SOURCE_FOLDER)
                        if relative_path == '.':
                            relative_path = ""
                        if self.uploader.upload_file(path, relative_path):
                            item_info['processed'] = True
                            self.pending_items.pop(path)
                    else:
                        logger.debug(f"Still waiting for: {os.path.basename(path)}")
                    
            except Exception as e:
                logger.error(f"Error checking item {os.path.basename(path)}: {e}")
    
    def _process_directory(self, dir_path):
        try:
            relative_path = os.path.relpath(dir_path, SOURCE_FOLDER)
            logger.info(f"Processing directory: {relative_path}")
            
            for root, _, files in os.walk(dir_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_relative_path = os.path.relpath(root, SOURCE_FOLDER)
                    
                    if file_path in self.pending_items and self.pending_items[file_path]['processed']:
                        continue
                    
                    self._handle_new_item(file_path, False)
                    self.check_pending_items()
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"Error processing directory {dir_path}: {e}")

def send_email(subject, body):
    try:
        msg = EmailMessage()
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject
        msg.set_content(body)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info("Email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

def main():
    logger.info("Starting FTP uploader script")
    logger.info(f"Monitoring {SOURCE_FOLDER}")
    logger.info(f"Destination: ftp://{FTP_SERVER}{FTP_FOLDER}")
    
    uploader = FTPUploader()
    monitor = FolderMonitor(uploader)  # Now properly passes uploader
    observer = Observer()
    
    try:
        observer.schedule(monitor, SOURCE_FOLDER, recursive=True)
        observer.start()
        
        # Initial scan
        for root, dirs, files in os.walk(SOURCE_FOLDER):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                monitor._handle_new_item(dir_path, True)
            for file in files:
                file_path = os.path.join(root, file)
                monitor._handle_new_item(file_path, False)
        
        while True:
            monitor.check_pending_items()
            
            if time.time() - uploader.last_activity > 3600:
                logger.warning("No activity for 1 hour - restarting FTP connection")
                uploader.connect()
                uploader.last_activity = time.time()
                
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("\nReceived keyboard interrupt - stopping")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        observer.stop()
        observer.join()
        uploader.close()
        logger.info("Cleanup complete. Exiting.")
        send_email("FTP Upload Script Completed", "All file uploads completed")

if __name__ == "__main__":
    main()
