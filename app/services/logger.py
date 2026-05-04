import logging
import os
from datetime import datetime

class AppLogger:
    def __init__(self):
        self.logs = []
        self.max_logs = 100

    def info(self, message):
        entry = {"time": datetime.now().strftime("%H:%M:%S"), "level": "INFO", "message": message}
        self.logs.insert(0, entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop()
        print(f"[INFO] {message}")

    def error(self, message):
        entry = {"time": datetime.now().strftime("%H:%M:%S"), "level": "ERROR", "message": message}
        self.logs.insert(0, entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop()
        print(f"[ERROR] {message}")

    def get_logs(self):
        return self.logs

logger = AppLogger()
