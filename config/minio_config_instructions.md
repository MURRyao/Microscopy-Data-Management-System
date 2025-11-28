# MinIO Configuration Instructions (Draft)

This document describes the basic steps required to configure MinIO for use in the Microscopy Data Management System. The current version is a placeholder and will be expanded later.

## 1. Accessing MinIO Console

After running the project's infrastructure via Docker Compose, the MinIO web console becomes available at:

http://localhost:9001

Use the credentials specified in the `docker-compose.yml` file.

## 2. Creating a Bucket

Create a new bucket that will store microscopy images. The recommended bucket name is:

microscopy-images

Further bucket structure conventions will be added later.

## 3. Connecting to MinIO Programmatically

Below is a basic template for connecting to MinIO using a Python SDK. Full examples will be added in future updates.

```python
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="YOUR_ACCESS_KEY",
    secret_key="YOUR_SECRET_KEY",
    secure=False
)
