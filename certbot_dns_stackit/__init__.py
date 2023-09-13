"""
certbot_dns_stackit.

-------------------

This module provides functionality to integrate STACKIT DNS with Certbot
for DNS-01 challenge type. The module contains two main classes:

- Authenticator: This class is responsible for solving the DNS-01 challenge by uploading
  the required validation token to a STACKIT DNS record.

- _StackitClient: This is an internal helper class that facilitates interactions
  with the STACKIT DNS API.

Note:
    The `_StackitClient` class is intended for internal use within this module and
    may not provide a stable public API for external consumers.

Examples:
    To use the `Authenticator` class for DNS-01 challenge:

    ```python
    authenticator = Authenticator(config, name)
    authenticator.perform(domain, validation_name, validation)
    ```

For further details on each class and their methods, refer to their respective docstrings.

"""

from .stackit import Authenticator

__all__ = ["Authenticator"]
