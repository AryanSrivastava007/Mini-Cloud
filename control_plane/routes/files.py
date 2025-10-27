import os
from fastapi import APIRouter, UploadFile, File, HTTPException
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from pydantic import BaseModel

router = APIRouter(prefix="/files", tags=["files"])

BUCKET = os.getenv("MINIO_BUCKET", "uploads")
AK = os.getenv("MINIO_ACCESS_KEY", "minicloud")
SK = os.getenv("MINIO_SECRET_KEY", "minicloud123")
ENDPOINT_INTERNAL = os.getenv("MINIO_ENDPOINT_INTERNAL", "http://minio:9000")
ENDPOINT_PUBLIC  = os.getenv("MINIO_ENDPOINT_PUBLIC", "http://localhost:9000")

def s3_client(endpoint):
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=AK,
        aws_secret_access_key=SK,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

s3_in  = s3_client(ENDPOINT_INTERNAL)
s3_pub = s3_client(ENDPOINT_PUBLIC)

def ensure_bucket():
    try:
        s3_in.head_bucket(Bucket=BUCKET)
    except ClientError:
        s3_in.create_bucket(Bucket=BUCKET)

@router.get("/ping")
def ping():
    return {"ok": True}

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    ensure_bucket()
    body = await file.read()
    safe_name = file.filename.replace(" ", "_")
    s3_in.put_object(
        Bucket=BUCKET, Key=safe_name, Body=body,
        ContentType=file.content_type or "application/octet-stream"
    )
    return {"ok": True, "filename": safe_name}

@router.get("/list/")
def list_files():
    ensure_bucket()
    resp = s3_in.list_objects_v2(Bucket=BUCKET)
    return {"files": [o["Key"] for o in resp.get("Contents", [])]}



class FileReq(BaseModel):
    filename: str

@router.post("/download")
def download_file_json(req: FileReq):
    ensure_bucket()
    url = s3_pub.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": req.filename},
        ExpiresIn=3600,
    )
    return {"url": url}

@router.get("/download/{filename}")
def download_file(filename: str):
    ensure_bucket()
    try:
        url = s3_pub.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": filename},
            ExpiresIn=3600,
        )
        return {"url": url}
    except Exception as e:
        raise HTTPException(500, f"Presign failed: {e}")


@router.delete("/{filename}")
def delete_file(filename: str):
    ensure_bucket()
    s3_in.delete_object(Bucket=BUCKET, Key=filename)
    return {"ok": True, "deleted": filename}
