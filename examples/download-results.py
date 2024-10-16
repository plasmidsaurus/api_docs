"""
Description: Download results from Plasmidsaurus
    - The "results" folder contains the .fasta/.gbk/reporting files. There are no "results" for custom sequencing projects.
    - The "reads" folder contains the raw reads (.fastq)

Usage:
    python download-results.py --item_code <item_code>

Required packages:
    - requests

"""

import os
import argparse
from utils import get_access_token, download_results

###### SETUP ######
# Save your client id and client secret in your environment variables
CLIENT_ID = os.getenv("PLASMIDSAURUS_CLIENT_ID")
CLIENT_SECRET = os.getenv("PLASMIDSAURUS_CLIENT_SECRET")
DESTINATION_DIR = "./data"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download results from Plasmidsaurus")
    parser.add_argument(
        "--item_code", type=str, help="The code of the item to download results for"
    )
    parser.add_argument(
        "--data_dir",
        type=str,
        default=DESTINATION_DIR,
        help="The directory to download the results to",
    )
    args = parser.parse_args()
    os.makedirs(args.data_dir, exist_ok=True)

    access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)
    download_results(args.item_code, access_token, args.data_dir)
