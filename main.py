import urllib3
from dotenv import load_dotenv
from pydantic import SecretStr

from client.direct_client import DirectClient
import os

from client.dnr_client import DNRClient
from schemas.schemas import LoginInfo, BucketInfo

load_dotenv()

config = os.environ
current_directory = os.getcwd()

if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    direct_client = DirectClient(
        base_url=config["DIRECT_BASE_URL"],
        login_info=LoginInfo(
            email=config["USER_EMAIL"],
            password=SecretStr(config["USER_PASSWORD"]),
        ),
    )
    direct_client.login()

    dnr_client = DNRClient(
        solver_url=config["DNR_SOLVER_URL"],
        fetch_bucket_info=BucketInfo(
            access_key_id=config["AWS_PROD_ACCESS_KEY"],
            secret_key=config["AWS_PROD_SECRET_KEY"],
            bucket_name=config["PROD_BUCKET_NAME"],
        ),
        upload_bucket_info=BucketInfo(
            access_key_id=config["AWS_STAGING_ACCESS_KEY"],
            secret_key=config["AWS_STAGING_SECRET_KEY"],
            bucket_name=config["STAGING_BUCKET_NAME"],
        ),
    )

    dnr_client.run_dnr_simulation(
        correlation_id="YOUR CORRELATION ID HERE",
        skip_download=True,
    )
