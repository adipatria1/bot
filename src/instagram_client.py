import os
import time
import random
import threading
from instagrapi import Client
from datetime import datetime
from .user_manager import user_manager
from .multi_post_manager import MultiPostManager

class InstagramClient:
    def __init__(self):
        self.client = None
        self.last_login = None
        self.login_attempts = 0
        self.max_login_attempts = 3
        self.login_cooldown = 300
        self.last_dm_time = 0
        self.dm_cooldown = 60
        self.bot_thread = None
        self.bot_running = False
        self.current_username = None

    def ensure_login(self):
        try:
            if not self.client or not self.current_username:
                self.client = Client()
                self.client.delay_range = [3, 5]
                
            if not self.client.user_id or (self.last_login and time.time() - self.last_login > 3600):
                if self.login_attempts >= self.max_login_attempts:
                    if time.time() - self.last_login < self.login_cooldown:
                        raise Exception("Too many login attempts. Please wait before trying again.")
                    self.login_attempts = 0

                username = self.current_username
                if not username:
                    raise Exception("No username set")
                    
                password = os.getenv(f'INSTA_PASSWORD_{username}')
                if not password:
                    raise Exception("Password not found for user")

                self.client.login(username=username, password=password)
                self.last_login = time.time()
                self.login_attempts = 0
                print(f"Successfully logged in as {username}")
                return True

            try:
                self.client.user_info(self.client.user_id)
                return True
            except Exception:
                self.client = None
                return self.ensure_login()

        except Exception as e:
            print(f"Login error: {e}")
            self.login_attempts += 1
            self.client = None
            raise

    def set_current_user(self, username):
        self.current_username = username
        self.client = None  # Force re-login with new user
        self.last_login = None

    def send_dm(self, user_id, message):
        current_time = time.time()
        if current_time - self.last_dm_time < self.dm_cooldown:
            sleep_time = self.dm_cooldown - (current_time - self.last_dm_time)
            time.sleep(sleep_time)
        
        try:
            if not self.ensure_login():
                raise Exception("Not logged in")
                
            time.sleep(random.uniform(2, 4))
            result = self.client.direct_send(message, [user_id])
            self.last_dm_time = time.time()
            return result
        except Exception as e:
            print(f"DM error: {e}")
            if "feedback_required" in str(e):
                print("DM rate limit hit, increasing cooldown")
                self.dm_cooldown = min(self.dm_cooldown * 2, 300)
            raise

    def start_bot(self):
        if not self.bot_running:
            self.bot_running = True
            self.bot_thread = threading.Thread(target=self.run_bot)
            self.bot_thread.daemon = True
            self.bot_thread.start()

    def stop_bot(self):
        self.bot_running = False
        if self.bot_thread:
            self.bot_thread.join()
            self.bot_thread = None

    def run_bot(self):
        processed_comments = set()
        dm_queue = []
        
        while self.bot_running:
            try:
                if not self.ensure_login():
                    time.sleep(60)
                    continue

                if dm_queue:
                    try:
                        dm_data = dm_queue[0]
                        self.send_dm(dm_data['user_id'], dm_data['message'])
                        dm_queue.pop(0)
                        time.sleep(random.uniform(30, 45))
                    except Exception as e:
                        print(f"Failed to send DM: {e}")
                        time.sleep(60)
                    continue

                if not self.current_username:
                    time.sleep(60)
                    continue

                post_manager = MultiPostManager(self.current_username)
                posts = post_manager.get_posts()
                
                for post_id, post_data in posts.items():
                    if not post_data['active']:
                        continue
                        
                    try:
                        media_id = self.client.media_pk_from_url(post_data['url'])
                        comments = self.client.media_comments(media_id)
                        
                        for comment in comments:
                            if comment.user.username == self.current_username:
                                continue
                                
                            if comment.pk not in processed_comments:
                                if not post_data.get('send_dm_if_keyword', False) or post_data['keyword'].lower() in comment.text.lower():
                                    processed_comments.add(comment.pk)
                                    username_to_reply = comment.user.username
                                    
                                    is_following = self.client.user_following(self.client.user_id, comment.user.pk)
                                    send_dm = (post_data.get('send_dm_if_following', False) and is_following) or (not post_data.get('send_dm_if_following', False) and not is_following)
                                    
                                    reply_text = post_data['reply_comment_text'].format(
                                        keyword=post_data['keyword'].upper(),
                                        username=username_to_reply
                                    )
                                    
                                    self.client.media_comment(media_id, reply_text, replied_to_comment_id=comment.pk)
                                    self.client.comment_like(comment.pk)
                                    
                                    if send_dm:
                                        commenter_info = self.client.user_info(comment.user.pk)
                                        commenter_display_name = commenter_info.full_name if commenter_info.full_name else "User"
                                        dm_text = post_data['reply_dm_text'].format(
                                            keyword=post_data['keyword'].upper(),
                                            display_name=commenter_display_name
                                        )
                                        dm_text = dm_text.replace("\\n", "\n")
                                        dm_queue.append({
                                            'user_id': comment.user.pk,
                                            'message': dm_text
                                        })
                                        
                                    post_data['last_check'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    post_manager.save_posts()
                                    
                    except Exception as e:
                        print(f"Error processing post {post_id}: {e}")
                        if "login_required" in str(e):
                            self.client = None
                        
                time.sleep(random.uniform(20, 40))
                
            except Exception as e:
                print(f"Bot error: {e}")
                time.sleep(60)
                
        print("Bot stopped")