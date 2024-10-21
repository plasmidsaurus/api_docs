import sys
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import zipfile

###### GLOBALS ######
API_URL = "https://plasmidsaurus.com"


###### HELPER FUNCTIONS ######
def download_file(url: str, output_file: str):
    """
    Download a file from a given URL and save it to a specified output file,
    showing a simple progress indicator.

    Args:
        url (str): The URL of the file to download.
        output_file (str): The path to save the downloaded file.
    """
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Check for HTTP errors

    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 KB
    downloaded = 0
    progress_bar_size = 50

    with open(output_file, "wb") as file:
        # Write to the file in chunks
        for data in response.iter_content(chunk_size=block_size):
            size = file.write(data)

            # Update the progress bar
            downloaded += size
            done = int(progress_bar_size * downloaded / total_size)
            sys.stdout.write(
                f"\r[{'=' * done}{' ' * (progress_bar_size-done)}] {downloaded}/{total_size} bytes"
            )
            sys.stdout.flush()

    print(f"\nFile downloaded successfully: {output_file}")


def unzip_file(zip_file: str, output_dir: str):
    """
    Unzip a file and extract its contents to a specified directory.

    Args:
        zip_file (str): Path to the zipe file
        output_dir (str): The path to the directory to extract the contents to.
    """
    print(f"Unzipping {zip_file} to {output_dir}")
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(output_dir)


def get_access_token(client_id: str, client_secret: str):
    """
    Get an access token
    """

    payload = {"grant_type": "client_credentials", "scope": "item:read"}
    res = requests.post(
        f"{API_URL}/oauth/token",
        data=payload,
        auth=HTTPBasicAuth(client_id, client_secret),
    )
    res.raise_for_status()
    return res.json()["access_token"]


def download_results(item_code: str, access_token: str, destination_dir: str):
    """
    Download results for a given item code
    """

    res = requests.get(
        f"{API_URL}/api/item/{item_code}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(f"ITEM {item_code}")
    res.raise_for_status()
    pprint(res.json())
    print("\n\n")

    # Download the results for this item
    print(f"DOWNLOADING RESULTS FOR {item_code} \n")
    res = requests.get(
        f"{API_URL}/api/item/{item_code}/results",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if res.ok:
        filename = Path(destination_dir) / f"{item_code}_results.zip"
        download_file(res.json()["link"], filename)
        unzip_file(filename, Path(destination_dir) / f"{item_code}_results")
    else:
        print(f"No results found for {item_code}: {res.content}")

    # Download the reads for this item
    print(f"DOWNLOADING READS FOR {item_code} \n")
    res = requests.get(
        f"{API_URL}/api/item/{item_code}/reads",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if res.ok:
        filename = Path(destination_dir) / f"{item_code}_reads.zip"
        download_file(res.json()["link"], filename)
        unzip_file(filename, Path(destination_dir) / f"{item_code}_reads")
    else:
        print(f"No reads found for {item_code}: {res.content}")


def get_items(access_token: str):
    """
    Get the latest item codes from the database. The API will return the most recent item first.
    """
    res = requests.get(
        f"{API_URL}/api/items",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    res.raise_for_status()
    user_items = res.json()

    res = requests.get(
        f"{API_URL}/api/items?shared=true",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    res.raise_for_status()
    shared_items = res.json()

    return user_items + shared_items
