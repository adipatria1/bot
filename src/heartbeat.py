import os
import time
from datetime import datetime

class HeartbeatMonitor:
    def __init__(self, heartbeat_dir='heartbeat'):
        self.heartbeat_dir = heartbeat_dir
        if not os.path.exists(heartbeat_dir):
            os.makedirs(heartbeat_dir)
            
    def update(self, username):
        heartbeat_file = os.path.join(self.heartbeat_dir, f'{username}_heartbeat.txt')
        with open(heartbeat_file, 'w') as f:
            f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
    def get_last_beat(self, username):
        heartbeat_file = os.path.join(self.heartbeat_dir, f'{username}_heartbeat.txt')
        try:
            with open(heartbeat_file, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
