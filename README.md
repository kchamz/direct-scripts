# Direct Scripts 

### Dependencies
This was developed on python **3.11.6**

`pip install -r requirements.txt`

### Environment variables
Create a `.env` file that contains the following variables
```
DIRECT_BASE_URL=
USER_EMAIL=
USER_PASSWORD=
AWS_PROD_ACCESS_KEY=
AWS_PROD_SECRET_KEY=
PROD_BUCKET_NAME=
AWS_STAGING_ACCESS_KEY=
AWS_STAGING_SECRET_KEY=
STAGING_BUCKET_NAME=
DNR_SOLVER_URL=
```

### Direct Client
In order to use the `DirectClient`, create an instance of the object
```
direct_client = DirectClient(
    base_url=config["DIRECT_BASE_URL"],
    login_info=LoginInfo(
        email=config["USER_EMAIL"],
        password=SecretStr(config["USER_PASSWORD"]),
    ),
)
```
It is enough to login once before calling any other function
```
direct_client.login()
```
Call any other function.
Most functions will have default payloads if none are provided.
**Example:**
```
proposal_item = direct_client.create_proposal_item()
proposal_item_id = proposal_item["id"]
```

### DNR Client

`DNRClient` allows to download DNR files stored in S3 using only the correlation id.
The downloaded files will hit the `fetch_bucket_info`.
It will download all the following files in the root directory of the project under a folder with correlation id as a name.
- raw_screen_usage.csv
- request.json
- solution_values.csv
- model.mps


It also allows to run a simulation of DNR on a dev enviroment using a correlation id **already ran** in prod (its files already exist).
To do so, `fetch_bucket_info` should point to PROD.
`upload_bucket_info` and `solver_url` should point to a dev environment such as staging.

`DNRClient` will download the files from the `fetch_bucket_info`, and will make a request to the `solver_url` using the downloaded `request.json` payload.
Once a *correlation_id* is provided by DNR, the `raw_screen_usage.csv`  will be uploaded to `upload_bucket_info` S3 bucket.
This will emulate as if Direct made the DNR call in a dev environment.

DNR will then be able to calculate a result.

In order to use the `DNRClient`, create an instance of the object
```
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
```

To download files
```
dnr_client.download_file(
    correlation_id="YOUR CORRELATION ID HERE",
    prefix="2024-01-01",  # A prefix if you already know which date you are searching
    search_scope=DNRS3SearchScopeLevel.day,  # A search scope for the current, year, month, or day
)
```

To run a DNR simulation
```
dnr_client.run_dnr_simulation(
    correlation_id="YOUR CORRELATION ID HERE",
    prefix="2024-01-01",  # A prefix if you already know which date you are searching
    search_scope=DNRS3SearchScopeLevel.day,  # A search scope for the current, year, month, or day
)
```

Explaining some parameters:
 - **prefix**: If you already know the prefix of the files (the date of the correlation ID).
 - **search_scope**: If you don't know the prefix of the files, the files were not uploaded through CloudDNR, and you just want to scope down your search to the current year, year & month, year & month & day.
 - **skip_download**: If the files are already downloaded are their designated path (the path that the script determines).