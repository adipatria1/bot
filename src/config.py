import os
from dotenv import load_dotenv, set_key

load_dotenv()

def update_env_file(key, value):
    dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
    set_key(dotenv_path, key, value)
    os.environ[key] = value