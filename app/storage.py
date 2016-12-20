import datetime
from google.cloud import storage

bucket_name = "instabattle_storage"
storage_client = storage.Client()
bucket = storage_client.get_bucket(bucket_name)

def list_blobs():
    """Lists all the blobs in the bucket."""
    blobs = bucket.list_blobs()

    for blob in blobs:
        print(blob.name)


def upload_blob(source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print('File {} uploaded to {}.'.format(
        source_file_name,
        destination_blob_name))


def download_blob(source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))


def delete_blob(blob_name):
    """Deletes a blob from the bucket."""
    blob = bucket.blob(blob_name)

    blob.delete()

    print('Blob {} deleted.'.format(blob_name))


def blob_metadata(blob_name):
    """Prints out a blob's metadata."""
    blob = bucket.get_blob(blob_name)

    print('Blob: {}'.format(blob.name))
    print('Bucket: {}'.format(blob.bucket.name))
    print('Storage class: {}'.format(blob.storage_class))
    print('ID: {}'.format(blob.id))
    print('Size: {} bytes'.format(blob.size))
    print('Updated: {}'.format(blob.updated))
    print('Generation: {}'.format(blob.generation))
    print('Metageneration: {}'.format(blob.metageneration))
    print('Etag: {}'.format(blob.etag))
    print('Owner: {}'.format(blob.owner))
    print('Component count: {}'.format(blob.component_count))
    print('Crc32c: {}'.format(blob.crc32c))
    print('md5_hash: {}'.format(blob.md5_hash))
    print('Cache-control: {}'.format(blob.cache_control))
    print('Content-type: {}'.format(blob.content_type))
    print('Content-disposition: {}'.format(blob.content_disposition))
    print('Content-encoding: {}'.format(blob.content_encoding))
    print('Content-language: {}'.format(blob.content_language))
    print('Metadata: {}'.format(blob.metadata))

def generate_signed_url(blob_name):
    """Generates a signed URL for a blob.
    Note that this method requires a service account key file. You can not use
    this if you are using Application Default Credentials from Google Compute
    Engine or from the Google Cloud SDK.
    """
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        # This URL is valid for 1 hour
        expiration=datetime.timedelta(hours=1),
        # Allow GET requests using this URL.
        method='GET')

    print('The signed url for {} is {}'.format(blob.name, url))


def rename_blob(blob_name, new_name):
    """Renames a blob."""
    blob = bucket.blob(blob_name)

    new_blob = bucket.rename_blob(blob, new_name)

    print('Blob {} has been renamed to {}'.format(
        blob.name, new_blob.name))

