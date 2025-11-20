# Gunicorn configuration file
import multiprocessing

max_requests = 1000
max_requests_jitter = 50

log_file = "-"

bind = "0.0.0.0:3000"

worker_class = "uvicorn.workers.UvicornWorker"
# Usar solo 1 worker para evitar problemas de memoria compartida con captcha_store y login_store
workers = 1