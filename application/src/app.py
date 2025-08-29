from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response, PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry, multiprocess, start_http_server
import boto3
import logging
import os

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# Prometheus metrics
upload_counter = Counter('file_uploads_total', 'Total number of uploaded files')

# AWS S3 setup
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION'),
    endpoint_url=os.getenv('LOCALSTACK_URL', 'http://localstack:4566')
)
bucket_name = os.getenv('S3_BUCKET_NAME')


@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "OK"


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not bucket_name:
        raise HTTPException(status_code=500, detail="S3_BUCKET_NAME not set in environment")

    content = await file.read()
    # key = f"{int(round(__import__('time').time() * 1000))}_{file.filename}"
    key = file.filename

    try:
        s3.put_object(Bucket=bucket_name, Key=key, Body=content)
        upload_counter.inc()
        logger.info(f"Uploaded file to S3: {key}")
        return {"filename": file.filename, "url": f"s3://{bucket_name}/{key}"}
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
