"""
Description: This script will automatically fetch results for your items when they're ready.
    - You can add it to your crontab to run every 10 minutes
    - It will check if the results for any completed items are available in a local folder. If not, it will download the results+reads
    - The "results" folder contains the .fasta/.gbk/reporting files. There are no "results" for custom sequencing projects.
    - The "reads" folder contains the raw reads (.fastq)

Required packages:
    - requests

Add this to your crontab: (replace `auto-fetch-results.py` with the absolute path to the script)
*/10 * * * * python3 examples/auto-fetch-results.py


"""

import os
import argparse
from datetime import datetime, timezone
from utils import get_access_token, download_results, get_items


###### SETUP ######
# Save your client id and client secret in your environment variables
CLIENT_ID = os.getenv("PLASMIDSAURUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("PLASMIDSAURUS_CLIENT_SECRET")
DESTINATION_DIR = "./plasmidsaurus_data"
MAX_DOWNLOAD_PER_ITER = 3  # Max number of items to download per iteration. Prevents against API rate limiting.
# Only download results for items that were completed after this date
DOWNLOAD_RESULTS_AFTER = datetime(2024, 9, 1, tzinfo=timezone.utc)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download results from Plasmidsaurus")
    parser.add_argument(
        "--data_dir",
        type=str,
        default=DESTINATION_DIR,
        help="The directory to download the results to",
    )
    args = parser.parse_args()
    os.makedirs(args.data_dir, exist_ok=True)

    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    # Get the latest item codes from the database
    items = get_items(access_token)

    # Filter out items that are not ready
    items = [item for item in items if item["status"] == "complete"]
    items = [
        item
        for item in items
        if item["done_date"]
        and datetime.fromisoformat(item["done_date"]) > DOWNLOAD_RESULTS_AFTER
    ]

    # List the items that have already been downloaded
    downloaded_items = os.listdir(args.data_dir)
    not_downloaded_items = [
        item for item in items if item["code"] not in downloaded_items
    ]

    # Cap the number of items downloaded per iteration. If there are more items ready, they'll be fetched in the next iteration.
    not_downloaded_items = not_downloaded_items[:MAX_DOWNLOAD_PER_ITER]

    # Download the results for the items
    print(
        f"Downloading results for {len(not_downloaded_items)} items: {', '.join([item['code'] for item in not_downloaded_items])}"
    )
    for item in not_downloaded_items:
        item_data_dir = os.path.join(args.data_dir, item["code"])
        os.makedirs(item_data_dir, exist_ok=True)
        try:
            download_results(item["code"], access_token, item_data_dir)
        except Exception as e:
            print(f"Error downloading results for {item['code']}: {e}")

        # NOTE: Here is where you would add any additional custom logic (i.e. uploading to S3, starting a workflow, etc.)
