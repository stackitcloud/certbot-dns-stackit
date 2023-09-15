# Certbot DNS-STACKIT Authenticator Plugin

[![License](https://img.shields.io/badge/License-Apache2.0-blue.svg)](https://github.com/stackitcloud/certbot-dns-stackit/blob/main/LICENSE)
[![GitHub Release](https://img.shields.io/github/v/release/stackitcloud/certbot-dns-stackit.svg)](https://github.com/stackitcloud/certbot-dns-stackit/releases)
[![Python Version](https://img.shields.io/badge/Python-%3E=3.7-blue.svg)](https://www.python.org/downloads/)
[![Downloads](https://img.shields.io/pypi/dm/certbot-dns-stackit.svg)](https://pypi.org/project/certbot-dns-stackit/)
[![Code Size](https://img.shields.io/github/languages/code-size/stackitcloud/certbot-dns-stackit.svg)](https://github.com/stackitcloud/certbot-dns-stackit)
[![Contributors](https://img.shields.io/github/contributors/stackitcloud/certbot-dns-stackit.svg)](https://github.com/stackitcloud/certbot-dns-stackit/graphs/contributors)

The Certbot DNS-STACKIT Authenticator Plugin facilitates the procurement of SSL/TLS certificates from Let's Encrypt
utilizing the DNS-01 challenge methodology in conjunction with STACKIT as the designated DNS service provider. This
document elucidates the procedural steps for the installation and operational utilization of this plugin.

## Installation

To initialize the Certbot DNS-STACKIT Authenticator Plugin, deploy the following pip command:

```bash
pip install certbot-dns-stackit
```

## Usage

Upon successful integration of the plugin, it becomes viable to employ it with Certbot for the retrieval of SSL/TLS
certificates. The subsequent section delineates the pertinent arguments and their respective examples:

### Arguments

| Argument                            | Example Value     | Description                                                                                                                                                                     |
|-------------------------------------|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--authenticator`                   | dns-stackit       | Engages the STACKIT authenticator mechanism. This must be configured as dns-stackit. (Mandatory)                                                                                | 
| `--dns-stackit-credentials`         | ./credentials.ini | Denotes the directory path to the credentials file for STACKIT DNS. This document must encapsulate the dns_stackit_auth_token and dns_stackit_project_id variables. (Mandatory) |
| `--dns-stackit-propagation-seconds` | 900               | Configures the delay prior to initiating the DNS record query. A 900-second interval (equivalent to 15 minutes) is recommended. (Default: 900)                                  |

### Example

Below is a structured example detailing the application of Certbot in conjunction with the DNS-STACKIT
Authenticator Plugin to retrieve a certificate:

```bash
certbot certonly \
  --authenticator dns-stackit \
  --dns-stackit-credentials ./credentials.ini \
  --dns-stackit-propagation-seconds 900 \
  --server https://acme-v02.api.letsencrypt.org/directory \
  --agree-tos \
  --rsa-key-size 4096 \
  -d 'example.runs.onstackit.cloud' \
  -d '*.example.runs.onstackit.cloud'
```

For this example, example.runs.onstackit.cloud represents the designated domain (zone) for certificate procurement.

### Example of credentials.ini

To operationalize the plugin, it's imperative to curate a credentials.ini file encompassing your STACKIT DNS
credentials:

```ini
dns_stackit_auth_token = "your_token_here"
dns_stackit_project_id = "your_project_id_here"
```

It's crucial to replace "your_token_here" and "your_project_id_here" placeholders with the genuine STACKIT
authentication token and project ID. The token's associated service account necessitates project membership privileges
for record set creation.

## Test Procedures

- Unit Testing:
    ```bash
    make test
    ```

- Linting:
    ```bash
    make lint
    ```

## Contribute
See [CONTRIBUTING.md](https://github.com/stackitcloud/certbot-dns-stackit/blob/main/CONTRIBUTING.md)

