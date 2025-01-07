from minio import Minio
from io import BytesIO
from minio.commonconfig import REPLACE, CopySource

def setup_minio_client():
    """初始化並返回 MinIO 客戶端"""
    return Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )

def ensure_bucket_exists(client, bucket_name):
    """確保指定的儲存桶存在，如果不存在就創建"""
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        print(f"已建立儲存桶: {bucket_name}")

def upload_file(client, bucket_name, object_name, data):
    """上傳檔案到 MinIO（不包含 metadata）"""
    try:
        # 如果輸入是 bytes，轉換為 BytesIO
        if isinstance(data, bytes):
            data_stream = BytesIO(data)
            data_length = len(data)
        else:
            data_stream = data
            data.seek(0, 2)  # 移到檔案結尾
            data_length = data.tell()
            data.seek(0)  # 重置位置
        
        # 上傳檔案
        client.put_object(
            bucket_name,
            object_name,
            data=data_stream,
            length=data_length
        )
        print(f"成功上傳 {object_name} 到 {bucket_name}")
        return True
    except Exception as e:
        print(f"檔案上傳錯誤: {e}")
        return False

def update_object_metadata(client, bucket_name, object_name, metadata):
    """使用 copy_object 更新物件的 metadata"""
    try:
        # 使用 CopySource 指定源對象
        copy_source = CopySource(bucket_name, object_name)
        
        # 執行複製操作，更新 metadata
        result = client.copy_object(
            bucket_name,
            object_name,
            copy_source,
            metadata=metadata,
            metadata_directive=REPLACE
        )
        print(f"成功更新 {object_name} 的 metadata")
        return True
    except Exception as e:
        print(f"更新 metadata 錯誤: {e}")
        return False

def main():
    # 初始設定
    client = setup_minio_client()
    bucket_name = "test-bucket"
    ensure_bucket_exists(client, bucket_name)
    
    # 測試檔案上傳
    test_data = b"Hello MinIO!"
    object_name = "test-file2.txt"
    
    # 步驟 1: 上傳檔案（不包含 metadata）
    if upload_file(client, bucket_name, object_name, test_data):
        print("檔案上傳完成")
        
        # 步驟 2: 分開更新 metadata
        custom_metadata = {
            "api": "https://coffee.alexflipnote.dev/3tBGocDGqTI_coffee.jpg",
            "id": "1843"  # 轉換為字串，因為 MinIO 要求 metadata 值必須是字串
        }
        
        if update_object_metadata(client, bucket_name, object_name, custom_metadata):
            print("Metadata 更新完成")

if __name__ == "__main__":
    main()