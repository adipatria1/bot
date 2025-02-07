from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from instagrapi import Client
from .config import update_env_file
from .user_manager import user_manager
from .multi_post_manager import MultiPostManager
from .instagram_client import InstagramClient
from .logger import setup_logger

bp = Blueprint('routes', __name__)
instagram_client = InstagramClient()
logger = setup_logger()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or 'username' not in session:
            return redirect(url_for('routes.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Both username and password are required', 'error')
            return render_template('login.html')
        
        try:
            cl = Client()
            cl.login(username=username, password=password)
            session['logged_in'] = True
            session['username'] = username
            
            if not user_manager.user_exists(username):
                user_manager.add_user(username)
                logger.info(f"New user added: {username}")
                
            update_env_file(f'INSTA_USERNAME_{username}', username)
            update_env_file(f'INSTA_PASSWORD_{username}', password)
            
            instagram_client.set_current_user(username)
            instagram_client.start_bot()
            logger.info(f"User {username} logged in successfully")
            return redirect(url_for('routes.index'))
        except Exception as e:
            logger.error(f"Login failed for user {username}: {e}")
            flash(str(e), 'error')
    
    return render_template('login.html')

@bp.route('/logout')
def logout():
    username = session.get('username')
    instagram_client.stop_bot()
    session.pop('logged_in', None)
    session.pop('username', None)
    logger.info(f"User {username} logged out")
    return redirect(url_for('routes.login'))

@bp.route('/')
@login_required
def index():
    username = session.get('username')
    post_manager = MultiPostManager(username)
    return render_template('index.html', posts=post_manager.get_posts(), username=username)

@bp.route('/add_post', methods=['POST'])
@login_required
def add_post():
    username = session.get('username')
    post_manager = MultiPostManager(username)
    try:
        url = request.form.get('url')
        post_manager.add_post(
            url=url,
            keyword=request.form.get('keyword', 'gelud'),
            reply_comment_text=request.form.get('reply_comment_text', "Thank you for commenting '{keyword}', @{username}!"),
            reply_dm_text=request.form.get('reply_dm_text', "Hi {display_name}! Thanks for commenting '{keyword}'. Can I help you with anything?"),
            send_dm_if_following=request.form.get('send_dm_if_following') == 'on',
            send_dm_if_keyword=request.form.get('send_dm_if_keyword') == 'on'
        )
        logger.info(f"New post added by {username}: {url}")
        flash('Post added successfully!', 'success')
    except ValueError as e:
        logger.error(f"Failed to add post for user {username}: {e}")
        flash(str(e), 'error')
    return redirect(url_for('routes.index'))

@bp.route('/remove_post/<post_id>')
@login_required
def remove_post(post_id):
    username = session.get('username')
    post_manager = MultiPostManager(username)
    post_manager.remove_post(post_id)
    logger.info(f"Post {post_id} removed by user {username}")
    flash('Post removed successfully!', 'success')
    return redirect(url_for('routes.index'))

@bp.route('/toggle_post/<post_id>')
@login_required
def toggle_post(post_id):
    username = session.get('username')
    post_manager = MultiPostManager(username)
    post_manager.toggle_post(post_id)
    logger.info(f"Post {post_id} toggled by user {username}")
    return redirect(url_for('routes.index'))
