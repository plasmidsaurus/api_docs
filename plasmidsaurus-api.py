"""

###### API ENDPOINTS ######

NOTE: An "item code" is a unique identifier for an item you purchased/can access. This code is on your dashboard order table.

________________________________________________________________________________

POST /oauth/token - returns an access token for the API, using your client ID and secret
{
    "grant_type": "client_credentials",
    "scope": "item:read" # What permissions you want to grant to this token. Currently only item:read is supported
}

Returns:
{
    "access_token": "<token>"
}

Use this token to make requests to the other endpoints, by adding it as a HTTP Authorization header:
Authorization: Bearer <token>
________________________________________________________________________________

GET /items - returns a list of items you have access to (either your own items, or items shared with you by other users)

Returns:
[
    {
        "code": "ABC123",
        "done_date": "2024-07-01T00:00:00+00:00",
        "gross": 45.0,
        "product_name": "plasmid_high_copy",
        "quantity": 3,
        "status": "complete",
    }
]

________________________________________________________________________________

GET /item/<item_code> - returns details of a specific item

Returns:
{
    "code": "ABC123",
    "done_date": "2024-07-01T00:00:00+00:00",
    "gross": 45.0,
    "product_name": "plasmid_high_copy",
    "quantity": 3,
    "status": "complete",
}
________________________________________________________________________________

GET /item/<item_code>/samples - returns a list of samples for a specific item

Returns:
[
    {
        "assemblies": [{"coverage": 500.0, "length": 9322, "n_reads": 500}],
        "name": "sample_1",
        "status": "complete",
    }
]
________________________________________________________________________________

GET /item/<item_code>/results - returns a link to download the results (fasta, gbk, read histogram, etc.) for a specific item

Returns:
{
    "link": "<url>"
}
________________________________________________________________________________

GET /item/<item_code>/reads - returns a link to download the reads (fastq) for a specific item

Returns:
{
    "link": "<url>"
}
________________________________________________________________________________
"""

import os
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import zipfile

###### SETUP ######
# Save your client id and client secret in your environment variables
CLIENT_ID = os.getenv("PLASMIDSAURUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("PLASMIDSAURUS_CLIENT_SECRET")
API_URL = "https://plasmidsaurus.com"
DESTINATION_DIR = "./data"

os.makedirs(DESTINATION_DIR, exist_ok=True)


###### HELPER FUNCTIONS ######
def download_file(url: str, output_file: str):
    """
    Download a file from a given URL and save it to a specified output file.

    Args:
        url (str): The URL of the file to download.
        output_file (str): The path to save the downloaded file.
    """
    response = requests.get(
        url, stream=True
    )  # Stream to avoid loading the file into memory all at once
    response.raise_for_status()  # Check for HTTP errors

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive new chunks
                file.write(chunk)

    print(f"File downloaded successfully: {output_file}")


def unzip_file(zip_file: str, output_dir: str):
    """
    Unzip a file and extract its contents to a specified directory.

    Args:
        zip_file (str): Path to the zipe file
        output_dir (str): The path to the directory to extract the contents to.
    """
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(output_dir)


###### API REQUESTS ######


# First, we need to get an access token that allows us to make requests to the API
payload = {"grant_type": "client_credentials", "scope": "item:read"}

# Make the POST request to the token endpoint
res = requests.post(
    f"{API_URL}/oauth/token",
    data=payload,
    auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
)
res.raise_for_status()
access_token = res.json()["access_token"]


# List all my recent orders
res = requests.get(
    f"{API_URL}/api/items",
    headers={"Authorization": f"Bearer {access_token}"},
)
print("MY ITEMS")
res.raise_for_status()
pprint(res.json()[:3])
print("\n\n")


# Get a specific item
ITEM_CODE = "Z9SVSX"

res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}",
    headers={"Authorization": f"Bearer {access_token}"},
)
print(f"ITEM {ITEM_CODE}")
res.raise_for_status()
pprint(res.json())
print("\n\n")


res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}/samples",
    headers={"Authorization": f"Bearer {access_token}"},
)
print(f"SAMPLES FOR {ITEM_CODE}")
res.raise_for_status()
pprint(res.json()[:3])
print("\n\n")


# Download the results for this item
print(f"DOWNLOADING RESULTS FOR {ITEM_CODE} \n")
res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}/results",
    headers={"Authorization": f"Bearer {access_token}"},
)
res.raise_for_status()
filename = Path(DESTINATION_DIR) / f"{ITEM_CODE}_results.zip"
download_file(res.json()["link"], filename)
unzip_file(filename, Path(DESTINATION_DIR) / f"{ITEM_CODE}_results")

# Download the reads for this item
print(f"DOWNLOADING READS FOR {ITEM_CODE} \n")
res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}/reads",
    headers={"Authorization": f"Bearer {access_token}"},
)
res.raise_for_status()
filename = Path(DESTINATION_DIR) / f"{ITEM_CODE}_reads.zip"
download_file(res.json()["link"], filename)
unzip_file(filename, Path(DESTINATION_DIR) / f"{ITEM_CODE}_reads")
