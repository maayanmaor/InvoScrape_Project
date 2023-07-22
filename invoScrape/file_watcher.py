import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from invoice_ocr import process_file, dict_post
import json


class FileWatcher(FileSystemEventHandler):

    def on_created(self, event):
        if not event.is_directory:
            result_dict = process_file(event.src_path)
            print(result_dict)
            file_name = os.path.basename(event.src_path)
            result_dict_str = json.dumps(result_dict)
            dict_post(file_name, result_dict_str)

            try:
                new_file_path = os.path.join(r"C:\Web\files", file_name)
                shutil.copy2(event.src_path, new_file_path)  # copy the file to a new path with a new file name
                os.remove(event.src_path)  # delete the original file after processing
                print(f"{event.src_path} moved to {new_file_path} and deleted from the upload directory.")
            except FileNotFoundError:
                pass


def start_watching(path):
    event_handler = FileWatcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)

    # Scan existing files in the target folder before starting the observer
    existing_files = [os.path.join(path, file) for file in os.listdir(path)]
    for file_path in existing_files:
        if os.path.isfile(file_path):
            event_handler.on_created(FileSystemEvent(src_path=file_path))

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
