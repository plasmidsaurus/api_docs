# Plasmidsaurus API
You can use the Plasmidsaurus REST API to fetch your sequencing results. 

## Getting Started

Generate your service credentials on your [user profile](https://www.plasmidsaurus.com/user-info). You'll receive a Client ID and Client Secret. 

> **NOTE:** Store these in a secure location! To preserve your data privacy, we cannot recover your Client Secret if it is lost. 

The scripts in this repo assume that these variables are exported to your environment variables. 

```
export PLASMIDSAURUS_CLIENT_ID=[your client id]
export PLASMIDSAURUS_CLIENT_SECRET=[your client secret]

python3 examples/plasmidsaurus-api-intro.py

python3 examples/download-results.py --item_code ABC123
```

## Autofetch Results
If you'd like to automatically fetch results as soon as they're ready, export your client_id + client_secret to your environment, and add this to your crontab. It will save new data to a folder called `plasmidsaurus_data`.

```
*/10 * * * * python3 examples/auto-fetch-results.py
```

## Overview

### API Endpoints 

```
GET /items 
GET /items?shared=true

GET /item/<item_code>

GET /item/<item_code>/samples

GET /item/<item_code>/results

GET /item/<item_code>/reads


```


### Authentication and Data Security 
The Plasmidsaurus API uses the OAuth2.0 protocol to protect requests using JSON Web Tokens. Your service credentials (client ID + secret keypair) are used to redeem temporary access tokens, which can be used to make API requests. This is called the OAuth2.0 Client Credentials Grant Flow. 

### Examples 
The examples are mostly self contained files with minimal pip dependencies. They rely on some functions defined in `utils.py`. 