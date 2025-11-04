from google.cloud import storage
import os

def upload_to_gcs(local_file_path, destination_blob_name):
    """
    Uploads a file to the GCS bucket specified in the .env file.
    Relies on the GOOGLE_APPLICATION_CREDENTIALS environment variable being set.
    """
    try:
        bucket_name = os.environ.get("GCP_BUCKET_NAME")
        if not bucket_name:
            print("❌ Error: GCP_BUCKET_NAME environment variable not set.")
            return None
            
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)

        print(f"⬆️  Uploading '{local_file_path}' to gs://{bucket_name}/{destination_blob_name}...")
        blob.upload_from_filename(local_file_path)

        print(f"✅ File uploaded successfully.")
        # Return the GCS URI for storage in the database
        return f"gs://{bucket_name}/{destination_blob_name}"
    except Exception as e:
        print(f"❌ Failed to upload to GCS. Have you set the GOOGLE_APPLICATION_CREDENTIALS environment variable? Error: {e}")
        return None