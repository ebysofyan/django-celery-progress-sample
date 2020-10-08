import os
import tempfile

broker_url = "redis://localhost:6379/0"
result_backend = "redis://localhost:6379/0"
accept_content = ["pickle", "json", "msgpack", "yaml"]
task_ignore_result = False
