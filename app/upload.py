from app import app 
import boto3 


def uploadToS3(file, filename, bucket_name): 
    try: 
        # Get s3 obj 
        s3 = boto3.client(
            's3', 
            aws_access_key_id=app.config['S3_ACCESS_KEY'],
            aws_secret_access_key=app.config['S3_SECRET_KEY']
        )
        # Upload file 
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ACL": 'public-read',
                "ContentType": file.content_type
            }
        )
        return True 
    except: 
        return False 
    