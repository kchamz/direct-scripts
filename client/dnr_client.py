import gzip
import io
import json
import os
import re
import sys

import boto3
import requests

from exceptions.exceptions import CorrelationIDNotFound
from schemas.schemas import BucketInfo, DNRFileNames


class DNRClient:
    _root_path = os.path.dirname(os.path.abspath(sys.argv[0]))

    def __init__(
        self,
        solver_url: str,
        fetch_bucket_info: BucketInfo,
        upload_bucket_info: BucketInfo,
    ) -> None:
        self._solver_url = solver_url

        self._fetch_bucket_name = fetch_bucket_info.bucket_name
        self._upload_bucket_name = upload_bucket_info.bucket_name

        # Usually PROD.
        self._fetch_s3_client = boto3.client(
            "s3",
            aws_access_key_id=fetch_bucket_info.access_key_id,
            aws_secret_access_key=fetch_bucket_info.secret_key,
        )

        # Usually Staging.
        self._upload_s3_client = boto3.client(
            "s3",
            aws_access_key_id=upload_bucket_info.access_key_id,
            aws_secret_access_key=upload_bucket_info.secret_key,
        )

    def _find_files(self, correlation_id: str):
        # The raw screen usage file name is exactly the correlation id.
        # Using that we can find the date it was added to use as a prefix.
        try:
            raw_screen_usage_metadata = self._fetch_s3_client.head_object(
                Bucket=self._fetch_bucket_name, Key=correlation_id
            )
        except (Exception,) as e:
            raise CorrelationIDNotFound(f"Cannot find correlation id: {correlation_id}")

        last_modified_string = raw_screen_usage_metadata["LastModified"].strftime(
            "%Y-%m-%d"
        )

        paginator = self._fetch_s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(
            Bucket=self._fetch_bucket_name, Prefix=last_modified_string
        )

        raw_file_names = {"raw_screen_usage": correlation_id}

        pattern = rf".*{re.escape(correlation_id)}.*"
        for page in pages:
            if "Contents" in page:
                keys = [obj["Key"] for obj in page["Contents"]]

                for key in keys:
                    match = re.search(pattern, key)

                    if match:
                        if "request" in match.string:
                            raw_file_names["request"] = match.string
                        elif "response" in match.string:
                            raw_file_names["solution_values"] = match.string
                        elif "mps" in match.string:
                            raw_file_names["mps"] = match.string

        return DNRFileNames(**raw_file_names)

    def _download_and_save_file(self, file_name: str, output_path: str) -> None:
        print(f"Downloading {file_name}")

        raw_file = self._fetch_s3_client.get_object(
            Bucket=self._fetch_bucket_name, Key=file_name
        )

        raw_content = raw_file["Body"]

        with gzip.GzipFile(fileobj=raw_content) as gzipfile:
            print("Unzipping file...")
            content = gzipfile.read().decode()

        with open(output_path, "w") as local_file:
            local_file.write(content)

        print(f"File saved locally: {output_path}\n")

    def download_files(self, correlation_id: str) -> None:
        file_names = self._find_files(correlation_id=correlation_id)

        output_folder_path = os.path.join(self._root_path, correlation_id)

        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
            print("Directory created:", output_folder_path)
        else:
            print("Directory already exists:", output_folder_path)

        self._download_and_save_file(
            file_name=file_names.raw_screen_usage,
            output_path=os.path.join(output_folder_path, "raw_screen_usage.csv"),
        )

        self._download_and_save_file(
            file_name=file_names.request,
            output_path=os.path.join(output_folder_path, "request.json"),
        )

        self._download_and_save_file(
            file_name=file_names.solution_values,
            output_path=os.path.join(output_folder_path, "solution_values.csv"),
        )

        self._download_and_save_file(
            file_name=file_names.mps,
            output_path=os.path.join(output_folder_path, "model.mps"),
        )

    def run_dnr_simulation(
        self, correlation_id: str, skip_download: bool = False
    ) -> str:
        if not skip_download:
            self.download_files(correlation_id=correlation_id)

        with open(
            file=f"{os.path.join(self._root_path, correlation_id)}/request.json"
        ) as payload_file:
            payload = json.loads(payload_file.read())

        print(f"Sending request to {self._solver_url}")

        response = requests.post(
            url=self._solver_url,
            data=gzip.compress(json.dumps(payload).encode()),
            headers={"Content-Encoding": "gzip"},
            timeout=120,
        )

        new_correlation_id = response.json()["correlation_id"]
        print(f"Correlation ID is: {new_correlation_id}")

        print(f"Scanning raw screen usage file")

        with open(
            f"{os.path.join(self._root_path, correlation_id)}/raw_screen_usage.csv",
            "rb",
        ) as raw_su_file:
            file_content = raw_su_file.read()

            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as f_out:
                f_out.write(file_content)
            buf.seek(0)

            print(
                f"Uploading raw screen usages to S3 on bucket: {self._upload_bucket_name}"
            )

            self._upload_s3_client.upload_fileobj(
                buf, self._upload_bucket_name, new_correlation_id
            )

            print("Upload successful")

        return correlation_id
