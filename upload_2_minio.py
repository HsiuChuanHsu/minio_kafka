# test_minio_kafka.py
from minio import Minio
from io import BytesIO

import time

def setup_minio_client():
    return Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )



def upload_file_with_metadata():
    client = setup_minio_client()
    bucket_name = "test-bucket"
    
    # 確保 bucket 存在
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
    
    # 準備測試檔案和 metadata
    test_data = b"Hello MinIO!"
    data_stream = BytesIO(test_data)  # 將 bytes 轉換為 BytesIO 物件
    custom_metadata = {
        # "x-amz-meta-custom-field": "test-value",
        # "x-amz-meta-timestamp": str(int(time.time())),
        # "x-amz-meta-source": "python-test",
        "api": "https://coffee.alexflipnote.dev/3tBGocDGqTI_coffee.jpg",
        "id": 1843
    }
    
    # 上傳檔案
    client.put_object(
        bucket_name,
        "test-file_apiid.txt",
        data=data_stream,  # 使用 BytesIO 物件
        length=len(test_data),
        metadata=custom_metadata
    )
    client.put_object(
        'test-bucket2',
        "test-file_apiid.txt",
        data=data_stream,  # 使用 BytesIO 物件
        length=len(test_data),
        metadata=custom_metadata
    )
    print(f"Uploaded file with metadata: {custom_metadata}")



if __name__ == "__main__":
    print("Starting MinIO-Kafka test...")
    
    # 上傳帶有 metadata 的文件
    upload_file_with_metadata()

    
