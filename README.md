# Certbot DNS-STACKIT Authenticator Plugin

The Certbot DNS-Stackit Authenticator Plugin allows you to obtain SSL/TLS certificates from Let's Encrypt using the
DNS-01 challenge method with STACKIT as your DNS provider. This README provides detailed instructions on how to install
and use the plugin.

## Installation

You can install the Certbot DNS-STACKIT Authenticator Plugin using pip:

```bash
pip install certbot-dns-stackit
```

## Usage

Once the plugin is installed, you can use it with Certbot to obtain SSL/TLS certificates. Below are the available
arguments and examples of how to use them:

### Arguments

| Argument                            | Example Value     | Description                                                                                                                                                                 |
|-------------------------------------|-------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--authenticator`                   | dns-stackit       | Selects the STACKIT authenticator. It must be set to dns-stackit. (Required)                                                                                                | 
| `--dns-stackit-credentials`         | ./credentials.ini | Specifies the path to the file where the credentials for STACKIT DNS are stored. This file should contain the dns_stackit_auth_token and dns_stackit_project_id. (Required) |
| `--dns-stackit-propagation-seconds` | 900               | Sets the time to wait until the DNS record is queried. It is recommended to set this to 900 seconds (15 minutes) for safety. (Default: 900)                                 |

### Example

Here's an example of how to use Certbot with the Certbot DNS-STACKIT Authenticator Plugin to obtain a certificate:

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

where example.runs.onstackit.cloud is the domain (zone) for which you want to obtain a certificate.

### Example of credentials.ini

To use the plugin, you need to create a credentials.ini file that contains your STACKIT DNS credentials:

```ini
dns_stackit_auth_token = "your_token_here"
dns_stackit_project_id = "your_project_id_here"
```

Make sure to replace "your_token_here" and "your_project_id_here" with your actual STACKIT authentication token and
project ID. The service account that owns the token must have the project membership role in order to create record
sets.

## Test Procedures

- Unit Testing:
    ```bash
    make test
    ```

- Linting:
    ```bash
    make lint
    ```
