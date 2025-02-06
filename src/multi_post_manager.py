import json
import re
from datetime import datetime
import os
from collections import OrderedDict

class MultiPostManager:
    def __init__(self, username):
        self.username = username
        self.posts_file = f'posts_{username}.json'
        self.posts = OrderedDict()
        self.load_posts()

    def load_posts(self):
        try:
            with open(self.posts_file, 'r') as f:
                data = json.load(f)
                self.posts = OrderedDict(data)
        except FileNotFoundError:
            self.posts = OrderedDict()

    def save_posts(self):
        with open(self.posts_file, 'w') as f:
            json.dump(self.posts, f)

    def add_post(self, url, keyword, reply_comment_text, reply_dm_text, send_dm_if_following=False, send_dm_if_keyword=False):
        shortcode_match = re.search(r'(?:/p/|/reel/|/tv/)([^/?]+)', url)
        if not shortcode_match:
            raise ValueError("Invalid Instagram post URL format")
        
        post_id = shortcode_match.group(1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        new_post = {
            'url': url,
            'active': True,
            'added_at': timestamp,
            'last_check': None,
            'keyword': keyword,
            'reply_comment_text': reply_comment_text,
            'reply_dm_text': reply_dm_text,
            'send_dm_if_following': send_dm_if_following,
            'send_dm_if_keyword': send_dm_if_keyword
        }
        
        if post_id in self.posts:
            temp_posts = OrderedDict()
            for pid, post in self.posts.items():
                temp_posts[pid] = post
                if pid == post_id:
                    temp_posts[f"{post_id}_{timestamp}"] = new_post
            self.posts = temp_posts
        else:
            self.posts[post_id] = new_post
            
        self.save_posts()

    def remove_post(self, post_id):
        if post_id in self.posts:
            del self.posts[post_id]
            self.save_posts()

    def toggle_post(self, post_id):
        if post_id in self.posts:
            self.posts[post_id]['active'] = not self.posts[post_id]['active']
            self.save_posts()

    def get_posts(self):
        return self.posts