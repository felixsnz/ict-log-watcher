from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED
import time
from utils.logger import get_logger
from typing import Callable

class IctLogWatcher:
    def __init__(self, watch_directory:str, on_new_report: Callable):
        self.observer = Observer()
        self.watch_directory = watch_directory
        self.event_handler = IctLogHandler(on_new_report)
        self.logger = get_logger(__name__, __class__.__name__)

    def start(self):
        try:
            self.observer.schedule(self.event_handler, self.watch_directory, recursive=False)
            self.observer.start()
            
            try:
                while True:
                    #TODO trigger event to stop watchdog
                    time.sleep(5)
            except KeyboardInterrupt:
                self.observer.stop()
            self.observer.join()
        except Exception as e:
            self.logger.debug(f"directory that caused the error: {self.watch_directory}")
            self.logger.error(e)

class IctLogHandler(FileSystemEventHandler):
    def __init__(self, on_new_log):
        self.on_new_log = on_new_log
        self.logger = get_logger(__name__, __class__.__name__)

    def on_created(self, event:FileSystemEvent):
        try:
            if event.is_directory:
                return None

            if event.event_type == EVENT_TYPE_CREATED or event.event_type == EVENT_TYPE_MODIFIED:
                self.on_new_log(event.src_path)
        except Exception as e:
            self.logger.debug(f"event that raised exeption: {event}")
            self.logger.error(e)

