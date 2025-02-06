bind = "0.0.0.0:8000"
workers = 3
timeout = 120
keepalive = 5
errorlog = "gunicorn-error.log"
accesslog = "gunicorn-access.log"
loglevel = "info"