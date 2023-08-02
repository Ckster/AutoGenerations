import os
import urllib
from typing import Union

from google.cloud import storage
from google.api_core.exceptions import NotFound


PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))


class Secrets:
    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(PROJECT_DIR,
                                                                    'booming-cairn-380522-002e5ada4689.json')


class Storage(Secrets):
    def __init__(self):
        super(Storage, self).__init__()
        self.client = storage.Client()

    def upload_image(self, image_path: str, cloud_storage_path: str, bucket_name: str = 'auto_generations_shop') -> str:
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(cloud_storage_path)
        blob.upload_from_filename(image_path)

        return urllib.parse.quote(f'https://storage.googleapis.com/{bucket_name}/{cloud_storage_path}')

    def download_image(self, cloud_storage_path: str, out_dir: str, bucket_name: str = 'auto_generations_shop'):
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(cloud_storage_path)
        blob.download_to_filename(os.path.join(out_dir, os.path.basename(cloud_storage_path)))

    def download_most_recent_pipeline_image(self, bucket_name: str = 'auto_generations_shop') -> Union[None, str]:
        bucket = self.get_bucket(bucket_name)
        blobs = list(bucket.list_blobs(prefix='pipeline'))

        if not blobs:
            print(f"No images found in the folder 'pipeline'.")
            return

            # Sort the blobs by their last modification time in descending order
        blobs.sort(key=lambda x: x.updated, reverse=True)

        # Get the most recent blob (file)
        most_recent_blob = blobs[0]

        output_path = os.path.join(PROJECT_DIR, 'data', 'product_images', most_recent_blob.name.split('/')[-1])

        most_recent_blob.download_to_filename(output_path)

        return output_path

    def delete_file(self, file_path: str, bucket_name: str = 'auto_generations_shop'):
        bucket = self.get_bucket(bucket_name)
        blob = bucket.blob(file_path)
        if blob.exists():
            blob.delete()

    def get_bucket(self, bucket_name: str):
        try:
            bucket = self.client.get_bucket(bucket_name)
        except NotFound:
            bucket = self.client.create_bucket(bucket_name)

        return bucket
