import os
import time
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class BackupHandler(FileSystemEventHandler):
    def __init__(self, source_dir, backup_dir):
        self.source_dir = source_dir
        self.backup_dir = backup_dir

    def on_modified(self, event):
        if not event.is_directory:
            self.perform_backup()

    def on_created(self, event):
        if not event.is_directory:
            self.perform_backup()

    def perform_backup(self):
        # Use rsync for incremental backup
        subprocess.run(['rsync', '-av', '--delete', self.source_dir, self.backup_dir])

def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def start_monitoring(source_dir, backup_dir):
    event_handler = BackupHandler(source_dir, backup_dir)
    observer = Observer()
    observer.schedule(event_handler, path=source_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    source_directory = "/path/to/source"
    backup_directory = "/path/to/backup"
    start_monitoring(source_directory, backup_directory)