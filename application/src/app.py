from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response, PlainTextResponse, JSONResponse
from datetime import datetime,timezone
from prometheus_client import (
    Counter,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST
)
from prometheus_fastapi_instrumentator import Instrumentator
import boto3
import logging
import os
import psutil
import threading
import time
import multiprocessing

app = FastAPI()

# -------------------- Logging --------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Log to local file
log_file_path = "app.log"
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Add Prometheus counter for log lines
log_lines = Counter("log_lines_total", "Total number of log lines")

class PrometheusLogHandler(logging.Handler):
    def emit(self, record):
        log_lines.inc()

logger.addHandler(PrometheusLogHandler())

# -------------------- AWS S3 Setup --------------------
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    endpoint_url=os.getenv('LOCALSTACK_URL', 'http://localstack:4566')  # Optional: for local testing
)
bucket_name = os.getenv('S3_BUCKET_NAME')

# -------------------- Upload Logs to S3 --------------------
def upload_logs_to_s3(interval=5):  # Every 5 seconds
    while True:
        try:
            if os.path.exists(log_file_path) and os.path.getsize(log_file_path) > 0:
                timestamp = time.strftime('%Y-%m-%d_%H-%M-%S')
                s3_key = f"logs/{timestamp}.log"

                with open(log_file_path, "rb") as f:
                    s3.upload_fileobj(f, bucket_name, s3_key)

                # Clear the log file after upload
                open(log_file_path, "w").close()

                logger.info(f"Uploaded log file to S3: {s3_key}")
        except Exception as e:
            logger.warning(f"Failed to upload log file to S3: {e}")

        time.sleep(interval)

# -------------------- Custom Business Metrics --------------------
upload_counter = Counter('file_uploads_total', 'Total number of uploaded files', ['status'])
s3_total_objects = Gauge("s3_total_objects", "Total number of objects in S3 bucket")
s3_total_size = Gauge("s3_total_size_bytes", "Total size of S3 bucket in bytes")

# -------------------- Infrastructure Metrics --------------------
cpu_usage = Gauge("cpu_usage_percent", "CPU usage percent")
memory_usage = Gauge("memory_usage_percent", "Memory usage percent")
disk_read = Gauge("disk_read_bytes", "Disk read bytes")
disk_write = Gauge("disk_write_bytes", "Disk write bytes")
net_in = Gauge("network_in_bytes", "Network input bytes")
net_out = Gauge("network_out_bytes", "Network output bytes")

def collect_system_metrics():
    while True:
        try:
            cpu_usage.set(psutil.cpu_percent(percpu=False))
            memory_usage.set(psutil.virtual_memory().percent)

            disk = psutil.disk_io_counters()
            disk_read.set(disk.read_bytes)
            disk_write.set(disk.write_bytes)

            net = psutil.net_io_counters()
            net_in.set(net.bytes_recv)
            net_out.set(net.bytes_sent)
        except Exception as e:
            logger.warning(f"System metrics error: {e}")

        time.sleep(5)

threading.Thread(target=collect_system_metrics, daemon=True).start()

# -------------------- S3 Metrics --------------------
def collect_s3_metrics():
    while True:
        try:
            total_objects = 0
            total_size = 0

            paginator = s3.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket_name):
                contents = page.get('Contents', [])
                total_objects += len(contents)
                total_size += sum(obj['Size'] for obj in contents)

            s3_total_objects.set(total_objects)
            s3_total_size.set(total_size)
        except Exception as e:
            logger.warning(f"S3 metrics error: {e}")

        time.sleep(60)

if bucket_name:
    threading.Thread(target=collect_s3_metrics, daemon=True).start()
    threading.Thread(target=upload_logs_to_s3, daemon=True).start()

# -------------------- Instrumentator --------------------
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
)
instrumentator.instrument(app).expose(app)

# -------------------- CPU Stress Test --------------------
def cpu_stress_worker(duration_seconds: int):
    end_time = time.time() + duration_seconds
    while time.time() < end_time:
        _ = sum(i * i for i in range(10000))

# -------------------- Endpoints --------------------
@app.get("/health", response_class=JSONResponse)
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "app": {
            "name": "Simple_App",
            "version": "1.0.0"
        }
    }
@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not bucket_name:
        raise HTTPException(status_code=500, detail="S3_BUCKET_NAME not set")

    content = await file.read()
    key = f"files/{file.filename}"

    try:
        s3.put_object(Bucket=bucket_name, Key=key, Body=content)
        upload_counter.labels(status="success").inc()
        logger.info(f"Uploaded file to S3: {key}")
        return {"filename": key, "url": f"s3://{bucket_name}/{key}"}
    except Exception as e:
        upload_counter.labels(status="failure").inc()
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")

@app.get("/test", response_class=PlainTextResponse)
async def stress_test():
    """
    Runs a CPU stress test for 30 seconds using multiprocessing.
    """
    duration = 30  # seconds
    cpu_cores = multiprocessing.cpu_count()
    processes = []

    logger.info(f"Starting CPU stress test for {duration} seconds on {cpu_cores} cores.")

    for _ in range(cpu_cores):
        p = multiprocessing.Process(target=cpu_stress_worker, args=(duration,))
        p.start()
        processes.append(p)

    return f"CPU stress test started for {duration} seconds using {cpu_cores} processes."

# -------------------- Main --------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
