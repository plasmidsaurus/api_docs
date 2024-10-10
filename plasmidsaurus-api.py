import os
import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import zipfile

###### SETUP ######
# Save your client id and client secret in your environment variables
CLIENT_ID = os.getenv("PLASMIDSAURUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("PLASMIDSAURUS_CLIENT_SECRET")
API_URL = "https://plasmidsaurus.com"

###### HELPER FUNCTIONS ######


def download_file(url, output_file):
    response = requests.get(
        url, stream=True
    )  # Stream to avoid loading the file into memory all at once
    response.raise_for_status()  # Check for HTTP errors

    with open(output_file, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive new chunks
                file.write(chunk)

    print(f"File downloaded successfully: {output_file}")


def unzip_file(zip_file, output_dir):
    with zipfile.ZipFile(zip_file, "r") as zip_ref:
        zip_ref.extractall(output_dir)


###### API REQUESTS ######

# Set up the request payload
payload = {"grant_type": "client_credentials", "scope": "item:read"}

# Make the POST request to the token endpoint
response = requests.post(
    f"{API_URL}/oauth/token",
    data=payload,
    auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
)

# Check the response status and parse the token
if response.status_code == 200:
    token_data = response.json()
    access_token = token_data.get("access_token")
else:
    print("Failed to obtain token:", response.status_code, response.text)
    exit(1)

# List all my recent orders
res = requests.get(
    f"{API_URL}/api/items",
    headers={"Authorization": f"Bearer {access_token}"},
)
print("MY ITEMS")
pprint(res.json()[:3])
print("\n\n")


# Get a specific item
ITEM_CODE = "Z9SVSX"

res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}",
    headers={"Authorization": f"Bearer {access_token}"},
)
print(f"ITEM {ITEM_CODE}")
pprint(res.json())


res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}/samples",
    headers={"Authorization": f"Bearer {access_token}"},
)
print(f"SAMPLES FOR {ITEM_CODE}")
pprint(res.json()[:3])  # First 3 samples


# Download the results for this item
res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}/results",
    headers={"Authorization": f"Bearer {access_token}"},
)
print(f"DOWNLOADING RESULTS FOR {ITEM_CODE}")
filename = f"{ITEM_CODE}_results.zip"
download_file(res.json()["link"], filename)

# Unzip the file
unzip_file(filename, f"{ITEM_CODE}_results")

# Download the reads for this item
res = requests.get(
    f"{API_URL}/api/item/{ITEM_CODE}/reads",
    headers={"Authorization": f"Bearer {access_token}"},
)
print(f"DOWNLOADING READS FOR {ITEM_CODE}")
filename = f"{ITEM_CODE}_reads.zip"
download_file(res.json()["link"], filename)

# Unzip the file
unzip_file(filename, f"{ITEM_CODE}_reads")
