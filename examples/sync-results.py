"""
Description: This script will automatically list all the ready results.
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
DOWNLOAD_RESULTS_AFTER = datetime(2024, 9, 1, tzinfo=timezone.utc)
API_URL = "https://plasmidsaurus.com"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List Ready results from Plasmidsaurus")
    parser.add_argument(
        "--out-prefix",
        type=str,
        default="plasmidsaurus/ready_items"
    )
    args = parser.parse_args()
    
    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

    outdir = os.path.dirname(args.out_prefix)
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    if args.out_prefix.endswith(".csv"):
        args.out_prefix = args.out_prefix[:-4]

    if args.out_prefix.endswith(os.sep):
        args.out_prefix += "ready_items"    
        
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
    csv_lines_list = []
    # Store all the items in a CSV file
    if items:
        print("Detected items ready for download")
        for item in items:
            reads_url = f"{API_URL}/api/item/{item['code']}/reads"
            csv_line = f"{item['code']},{item['status']},{item['done_date']},{reads_url}\n"
            csv_lines_list.append(csv_line)
    
    csv_text = "".join(csv_lines_list)
    with open(f"{args.out_prefix}.csv", "w") as f:
        f.write("item_code,status,done_date,reads_url\n")
        f.write(csv_text)