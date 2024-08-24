from db_utils import Client, create_client
from supabase.client import ClientOptions
from db_utils import supabase_api

def upload_file(file_name, bucket, db_client=supabase_api):
    with open(file_name, "rb") as f:
        db_client.storage.from_(bucket).upload(
            file=f,
            path=file_name,
            file_options={"content-type": "image/jpeg"},
        )