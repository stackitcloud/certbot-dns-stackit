import logging
from dataclasses import dataclass
from typing import Optional, List, Callable

import requests
from certbot import errors
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)


@dataclass
class Record:
    """Represents a Record."""

    content: str
    id: str


@dataclass
class RRSet:
    """Represents a RRSet."""

    id: str
    records: List[Record]


class _StackitClient(object):
    """
    A client to interact with the STACKIT DNS API.

    Attributes:
        auth_token (str): The authentication token for the API.
        project_id (str): The project ID associated with the domain (zone).
        base_url (str): The base URL endpoint for the STACKIT API.
        headers (dict): The headers to be used in API requests.
    """

    def __init__(self, auth_token: str, project_id: str, base_url: str):
        """
        Initialize the StackitClient.

        :param auth_token: The authentication token for the API.
        :param project_id: The project ID associated with the domain (zone).
        :param base_url: The base URL endpoint for the STACKIT API.
        """
        self.auth_token = auth_token
        self.project_id = project_id
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}

    def add_txt_record(self, domain: str, validation_name: str, validation: str):
        """
        Add a TXT record using the supplied information.

        :param domain: The domain one level above the validation name.
        :param validation_name: The acme challenge record name.
        :param validation: The acme challenge record content.
        """
        zone_id = self._get_zone_id(domain)
        rrset = self._get_rrset(zone_id, validation_name)
        # rrset does not exist therefore add it
        if rrset is None:
            self._create_rrset(zone_id, validation_name, validation)
        else:
            # rrset exists. If it does not contain the validation record, add it
            records = [record.content for record in rrset.records]
            if validation not in records:
                self._add_record_to_rrset(zone_id, rrset.id, validation)

    def _create_rrset(self, zone_id: str, validation_name: str, validation: str):
        """
        Create a new rrset for the supplied zone id.

        :param zone_id: The zone ID where the rrset will be created.
        :param validation_name: The record name.
        :param validation: The record content.
        """
        # append a dot if the validation name does not end with a dot
        if not validation_name.endswith("."):
            validation_name = f"{validation_name}."

        body = {
            "name": validation_name,
            "type": "TXT",
            "ttl": 60,
            "records": [
                {
                    "content": validation,
                }
            ],
        }

        res = requests.post(
            f"{self.base_url}/v1/projects/{self.project_id}/zones/{zone_id}/rrsets",
            headers=self.headers,
            json=body,
        )

        if res.status_code != 202:
            raise errors.PluginError(
                f"Could not create rrset for zone id {zone_id}. Response: {res.text}"
            )

    def _add_record_to_rrset(self, zone_id: str, rrset_id: str, validation: str):
        """
        Add a record to an existing rrset.

        :param zone_id: The zone ID where the rrset is located.
        :param rrset_id: The rrset ID where the record will be added.
        :param validation: The record content.
        """
        body = {
            "action": "add",
            "records": [
                {
                    "content": validation,
                }
            ],
        }

        res = requests.patch(
            f"{self.base_url}/v1/projects/{self.project_id}/zones/{zone_id}/rrsets/{rrset_id}/records",
            headers=self.headers,
            json=body,
        )

        if res.status_code != 202:
            raise errors.PluginError(
                f"Could not add record to rrset {rrset_id}. Response: {res.text}"
            )

    def _get_zone_id(self, domain: str) -> str:
        """
        Retrieve the zone ID for the given domain.

        :param domain: The domain (zone dnsName) for which the zone ID is needed.
        :return: The ID of the zone.
        """
        parts = domain.split('.')

        # we are searching for the best matching zone. We can do that by iterating over the parts of the domain
        # from left to right.
        for i in range(len(parts)):
            subdomain = '.'.join(parts[i:])
            res = requests.get(
                f"{self.base_url}/v1/projects/{self.project_id}/zones?dnsName[eq]={subdomain}&active[eq]=true",
                headers=self.headers,
            )

            if res.status_code == 200 and len(res.json()["zones"]) > 0:
                return res.json()["zones"][0]["id"]

        raise errors.PluginError(
            f"Could not find zone id for domain {domain}, Response: {res.text}"
        )

    def _get_rrset(self, zone_id: str, validation_name: str) -> Optional[RRSet]:
        """
        Retrieve the rrset ID for the given zone ID and validation name.

        :param zone_id: The zone ID where the rrset is located.
        :param validation_name: The name of the rrset to retrieve.
        :return: The rrset object if found; otherwise, None.
        """
        if not validation_name.endswith("."):
            validation_name = f"{validation_name}."

        res = requests.get(
            f"{self.base_url}/v1/projects/{self.project_id}/zones/{zone_id}/rrsets?name[eq]={validation_name}&type[eq]=TXT&active[eq]=true",
            headers=self.headers,
        )
        if res.status_code != 200:
            raise errors.PluginError(
                f"Could not find rrset id for zone id {zone_id} and validation name {validation_name}, Response: {res.text}"
            )

        if len(res.json()["rrSets"]) == 0:
            return None

        records = []
        for record in res.json()["rrSets"][0]["records"]:
            records.append(Record(content=record["content"], id=record["id"]))

        rrset = RRSet(id=res.json()["rrSets"][0]["id"], records=records)

        return rrset

    def del_txt_record(self, domain: str, validation_name: str, validation: str):
        """
        Delete a TXT record using the supplied information.

        :param domain: The zone dnsName.
        :param validation_name: The record name.
        :param validation: The record content.
        """
        zone_id = self._get_zone_id(domain)
        rrset = self._get_rrset(zone_id, validation_name)
        # delete rrset only if it exists. If it does not exist, we do not need to delete it
        if rrset is not None:
            self._delete_record_set(zone_id, rrset.id)

    def _delete_record_set(self, zone_id: str, rrset_id: str):
        """
        Delete the rrset using the supplied zone ID and rrset ID.

        :param zone_id: The zone ID where the rrset is located.
        :param rrset_id: The ID of the rrset to be deleted.
        """
        res = requests.delete(
            f"{self.base_url}/v1/projects/{self.project_id}/zones/{zone_id}/rrsets/{rrset_id}",
            headers=self.headers,
        )

        if res.status_code != 202:
            raise errors.PluginError(
                f"Could not delete rrset id {rrset_id}. Response: {res.text}"
            )


class Authenticator(dns_common.DNSAuthenticator):
    """
    STACKIT DNS Authenticator.

    This authenticator resolves a DNS01 challenge by publishing the required
    validation token (record within a record set within a zone) to a STACKIT DNS record.

    Attributes:
        credentials: A configuration object that holds STACKIT API credentials.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the Authenticator by calling the parent's init method."""
        super(Authenticator, self).__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(cls, add: Callable, **kwargs):
        """
        Add custom arguments for the STACKIT DNS Authenticator.

        :param add: Callable to add an argument.
        :param kwargs: Additional keyword arguments.
        """
        super(Authenticator, cls).add_parser_arguments(
            add, default_propagation_seconds=900
        )
        add("credentials", help="STACKIT credentials INI file.")

    def _setup_credentials(self):
        """Set up and configure the STACKIT credentials."""
        self.credentials = self._configure_credentials(
            "credentials",
            "STACKIT credentials for the STACKIT DNS API",
            {
                "project_id": "Specifies the project id of the STACKIT project.",
                "auth_token": "Defines the authentication token for the STACKIT DNS API. Keep in mind that the "
                "service account to this token need to have project edit permissions as we create txt "
                "records in the zone",
            },
        )

    def _perform(self, domain: str, validation_name: str, validation: str):
        """
        Carry out a DNS update.

        :param domain: The domain where the DNS record will be added. Does not need to be the zone dns name but any domain.
        :param validation_name: The name of the DNS record.
        :param validation: The validation content to be added to the DNS record.
        """
        self._get_stackit_client().add_txt_record(domain, validation_name, validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str):
        """
        Remove the previously added DNS record.

        :param domain: The domain from which the DNS record will be deleted.
        :param validation_name: The name of the DNS record to be deleted.
        :param validation: The validation content of the DNS record to be deleted.
        """
        self._get_stackit_client().del_txt_record(domain, validation_name, validation)

    def _get_stackit_client(self) -> _StackitClient:
        """
        Instantiate and return a StackitClient object.

        :return: A _StackitClient instance to interact with the STACKIT DNS API.
        """
        base_url = "https://dns.api.stackit.cloud"
        if self.credentials.conf("base_url") is not None:
            base_url = self.credentials.conf("base_url")

        return _StackitClient(
            self.credentials.conf("auth_token"),
            self.credentials.conf("project_id"),
            base_url,
        )
