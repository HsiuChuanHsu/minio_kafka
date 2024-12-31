from confluent_kafka import Consumer, KafkaError
import json
from typing import Dict, Any
import time 

def setup_kafka_consumer() -> Consumer:
    conf = {
        'bootstrap.servers': 'localhost:9092',  # 修改連接地址
        'group.id': 'minio-test-group',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': True
    }
    return Consumer(conf)

def extract_minio_info(event_data: dict) -> dict:
    """
    從 MinIO 事件中提取所需資訊
    
    Args:
        event_data (dict): MinIO 事件數據
        
    Returns:
        dict: 包含 bucket_path, api_name, api_id 的字典
    """
    try:
        # 初始化返回字典
        result = {
            'bucket_path': '',
            'api_name': '',
            'api_id': ''
        }
        
        if 'Records' in event_data and event_data['Records']:
            record = event_data['Records'][0]
            
            # 獲取 bucket_path (bucket_name/object_key)
            bucket_name = record['s3']['bucket']['name']
            object_key = record['s3']['object']['key']
            result['bucket_path'] = f"{bucket_name}/{object_key}"
            
            # 從 userMetadata 中獲取 API 資訊
            if 'userMetadata' in record['s3']['object']:
                metadata = record['s3']['object']['userMetadata']
                result['api_name'] = metadata.get('X-Amz-Meta-Api', '')
                result['api_id'] = metadata.get('X-Amz-Meta-Id', '')
        
        return result
        
    except Exception as e:
        print(f"Error extracting info: {e}")
        return None

def process_message(msg: Dict[str, Any]) -> None:
    try:
        # MinIO 事件已經是 JSON 格式
        print("\nReceived MinIO event:")
        print(json.dumps(msg, indent=2))
        
        if 'Records' in msg:
            result = extract_minio_info(msg)
            print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error processing message: {e}")

def listen_kafka_events() -> None:
    try:
        consumer = setup_kafka_consumer()
        consumer.subscribe(['minio-events'])
        print("\nWaiting for messages...")
        
        # start_time = time.time()
        while True:
            # if time.time() - start_time > timeout:
            #     print(f"\nTimeout after {timeout} seconds")
            #     break
                
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                print(f"Error: {msg.error()}")
                continue
            
            try:
                value = json.loads(msg.value().decode('utf-8'))
                process_message(value)
            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e}")
            
    finally:
        consumer.close()
        print("\nKafka consumer closed")

if __name__ == "__main__":
    listen_kafka_events()