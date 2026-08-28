#!/usr/bin/env python3
"""
Render startup script: runs Alembic migrations and creates the MinIO bucket
if it doesn't already exist before the app starts.
"""
import subprocess
import sys
import os
import time


def run_migrations():
    print(">>> Running Alembic migrations...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd="/app/backend",
        capture_output=False,
    )
    if result.returncode != 0:
        print("ERROR: Migrations failed. Aborting startup.")
        sys.exit(1)
    print(">>> Migrations complete.")


def ensure_minio_bucket():
    """Create the storage bucket if it doesn't exist."""
    storage_bucket = os.environ.get("STORAGE_BUCKET", "spendshield-evidence")
    storage_endpoint = os.environ.get("STORAGE_ENDPOINT_URL", "")
    access_key = os.environ.get("STORAGE_ACCESS_KEY", "")
    secret_key = os.environ.get("STORAGE_SECRET_KEY", "")

    if not storage_endpoint or not access_key or not secret_key:
        print(">>> Storage env vars not set, skipping bucket creation.")
        return

    # Retry a few times in case MinIO is still starting
    for attempt in range(5):
        try:
            import boto3
            from botocore.client import Config
            from botocore.exceptions import ClientError

            s3 = boto3.client(
                "s3",
                endpoint_url=storage_endpoint,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key,
                config=Config(signature_version="s3v4"),
                region_name="us-east-1",
            )
            try:
                s3.head_bucket(Bucket=storage_bucket)
                print(f">>> Bucket '{storage_bucket}' already exists.")
            except ClientError as e:
                if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
                    s3.create_bucket(Bucket=storage_bucket)
                    print(f">>> Created bucket '{storage_bucket}'.")
                else:
                    raise
            return
        except Exception as exc:
            print(f">>> Storage not ready (attempt {attempt + 1}/5): {exc}")
            if attempt < 4:
                time.sleep(5)
            else:
                print(">>> WARNING: Could not connect to storage. Continuing anyway.")


if __name__ == "__main__":
    run_migrations()
    ensure_minio_bucket()
