import logging
import os
from datetime import datetime

class ClassnameFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt=None, style='%', classname=None):
        super().__init__(fmt, datefmt, style)
        self.classname = classname

    def format(self, record):
        if 'funcName' in record.__dict__:
            fn = record.__dict__['funcName']
            if self.classname is not None:
                fn = self.classname + "." + fn
            record.__dict__['funcName'] = fn
        return super().format(record)

class DailyFileHandler(logging.Handler):
    def __init__(self, log_dir, level=logging.NOTSET):
        super().__init__(level)
        self.log_dir = log_dir
        self.log_file = None
        self.handler = None
        self.today = datetime.now().date()

    def emit(self, record):
        if self.handler is None or datetime.now().date() != self.today:
            self.today = datetime.now().date()
            if self.handler is not None:
                self.handler.close()
            self.log_file = os.path.join(self.log_dir, f'{self.today.strftime("%d_%m_%Y")}.log')
            self.handler = logging.FileHandler(self.log_file)
            self.handler.setLevel(self.level)
            self.handler.setFormatter(self.formatter)
        self.handler.emit(record)

    def close(self):
        if self.handler is not None:
            self.handler.close()

# and update your get_logger function
def get_logger(name, class_name=None):
    # Create a logger
    logger = logging.getLogger(name)

    # Set the level of severity that will be logged
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    handler = DailyFileHandler(log_dir)
    handler.setLevel(logging.DEBUG)

    # Create a logging format
    formatter = ClassnameFormatter('%(asctime)s %(levelname)s %(name)s.%(funcName)s:%(lineno)d - %(message)s',
                                   datefmt='%Y-%m-%d %H:%M:%S', classname=class_name)
    handler.setFormatter(formatter)

    # Check if the logger already has the handler to avoid duplicate logs
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger