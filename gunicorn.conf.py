bind = "0.0.0.0:10000"
workers = 1
worker_class = "sync"
timeout = 180
keepalive = 2
max_requests = 100
max_requests_jitter = 10
preload_app = True