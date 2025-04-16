import boto3
import json

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Parameters
    bucket_name = 'yelp-sample-test'
    key = 'yelp_academic_dataset_review.json'
    output_prefix = 'chunks/split_file_'  # S3 key prefix
    num_files = 20  # Number of split files
    
    local_input_path = '/tmp/input.json'
    s3.download_file(bucket_name, key, local_input_path)
    
    # Count lines in the file
    with open(local_input_path, 'r', encoding='utf8') as f:
        total_lines = sum(1 for _ in f)

    lines_per_file = total_lines // num_files
    print(f"Total lines: {total_lines}, Lines per file: {lines_per_file}")
    
    # Re-open and split
    with open(local_input_path, 'r', encoding='utf8') as f:
        for i in range(num_files):
            chunk_lines = []
            for j in range(lines_per_file):
                line = f.readline()
                if not line:
                    break
                chunk_lines.append(json.loads(line))

            # Write chunk to temp file
            chunk_filename = f'/tmp/split_file_{i+1}.json'
            with open(chunk_filename, 'w', encoding='utf8') as out_file:
                json.dump(chunk_lines, out_file)

            # Upload to S3
            chunk_key = f"{output_prefix}{i+1}.json"
            s3.upload_file(chunk_filename, bucket_name, chunk_key)
            print(f"✅ Uploaded {chunk_key}")
    
    return {
        'statusCode': 200,
        'body': f"Successfully uploaded {num_files} split files to {bucket_name}/{output_prefix}"
    }
