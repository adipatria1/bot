import json
from datetime import datetime

class UserManager:
    def __init__(self):
        self.users = {}
        self.load_users()

    def load_users(self):
        try:
            with open('users.json', 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}

    def save_users(self):
        with open('users.json', 'w') as f:
            json.dump(self.users, f)

    def add_user(self, username):
        if username not in self.users:
            self.users[username] = {
                'added_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'posts_file': f'posts_{username}.json'
            }
            self.save_users()
            return True
        return False

    def get_user(self, username):
        return self.users.get(username)

    def user_exists(self, username):
        return username in self.users

user_manager = UserManager()