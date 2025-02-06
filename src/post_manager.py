import json
import re
from datetime import datetime

class PostManager:
    def __init__(self):
        self.posts = {}
        self.load_posts()

    def load_posts(self):
        try:
            with open('posts.json', 'r') as f:
                self.posts = json.load(f)
        except FileNotFoundError:
            self.posts = {}

    def save_posts(self):
        with open('posts.json', 'w') as f:
            json.dump(self.posts, f)

    def add_post(self, url, keyword, reply_comment_text, reply_dm_text, send_dm_if_following=False, send_dm_if_keyword=False):
        shortcode_match = re.search(r'(?:/p/|/reel/|/tv/)([^/?]+)', url)
        if not shortcode_match:
            raise ValueError("Invalid Instagram post URL format")
        
        post_id = shortcode_match.group(1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.posts[post_id] = {
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
        self.save_posts()

    def remove_post(self, post_id):
        if post_id in self.posts:
            del self.posts[post_id]
            self.save_posts()

    def toggle_post(self, post_id):
        if post_id in self.posts:
            self.posts[post_id]['active'] = not self.posts[post_id]['active']
            self.save_posts()

post_manager = PostManager()