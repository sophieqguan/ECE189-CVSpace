import os
import sys
from asyncio import sleep
from http import HTTPStatus

from dotenv import load_dotenv
from pprint import pprint

from cvat_sdk import make_client
from cvat_sdk.core.helpers import DeferredTqdmProgressReporter
from cvat_sdk.api_client import Configuration, ApiClient, exceptions
from cvat_sdk.api_client.models import *
import zipfile
import io

load_dotenv()

API_KEY = os.getenv("CVAT_API_KEY", "<authorization token>")
API_SESSIONID = os.getenv("CVAT_API_SESSIONID", "<session id>")
API_CSRFTOKEN = os.getenv("CVAT_API_CSRFTOKEN", "<csrf token>")

assert API_KEY and API_SESSIONID and API_CSRFTOKEN
# print(f"Token {API_KEY}")
with make_client("https://app.cvat.ai", port=443) as client:
    client.api_client.set_default_header("Authorization", f"Token {API_KEY}")
    client.api_client.cookies["sessionid"] = API_SESSIONID
    client.api_client.cookies["csrftoken"] = API_CSRFTOKEN
    # client.organization_slug = ""
    client.config.status_check_period = 2

api = client.api_client


def extract(zip_file, extract_to_path):
    with io.BytesIO(zip_file) as zip_buffer:
        # Open the zip file
        with zipfile.ZipFile(zip_buffer, 'r') as zip_ref:
            # Extract all contents to the specified folder
            zip_ref.extractall(extract_to_path)


def fetch(job_id):
    print(f"[Job {job_id}] Initiated request.")
    while True:
        (_, res) = api.jobs_api.retrieve_annotations(id=job_id,
                                                     format="YOLO 1.1",
                                                     _parse_response=False)
        if res.status == HTTPStatus.CREATED:
            break

    print(f"[Job {job_id}] Ready for download.")
    (_, res) = api.jobs_api.retrieve_annotations(id=job_id,
                                                 action="download",
                                                 format="YOLO 1.1",
                                                 use_default_location=True,
                                                 _parse_response=False)
    print(res.status)

    # output is a zip file
    extract(res.data, f'annotations/{job_id}')
    print(f"[Job {job_id}] Extracted to folders.")


def main(job_id, extract_all=True):
    try:
        if extract_all:
            jobs, response = api.jobs_api.list(stage="validation")
            for id, job in enumerate(jobs['results']):
                fetch(job['id'])
        else:
            fetch(job_id)
    except Exception as e:
        print("Exception: %s\n" % e)


if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            job_id = int(sys.argv[1])
            main(job_id, extract_all=False)
        else:
            main(None, extract_all=True)
    except ValueError:
        print("Error: Please enter a valid job id.")
        sys.exit(1)
