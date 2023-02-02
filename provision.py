#!/usr/bin/env python3

import logging
from sys import argv
from pathlib import Path
from dataclasses import asdict, dataclass, fields
from os import environ
from typing import Optional, Tuple

import requests
import yaml
from yaml.loader import SafeLoader

logging_format = "%(asctime)s %(message)s"
logging.basicConfig(level=logging.INFO, format=logging_format)


@dataclass
class ServiceItem:
    name: str  # My Service name
    domain: str  # https://statping.com
    expected: str = ""  # word to find in case of http check
    type: str = "http"  # one of http, tcp, udp, icmp, grpc, static
    method: str = "GET"  # http methods: GET, POST, PATCH, DELETE
    post_data: str = ""  # http body if type is http
    port: int = 0  # port if other than type: http, static, icmp
    expected_status: int = 200  # http response code
    check_interval: int = 30  # check interval, in seconds
    timeout: int = 30  # seconds
    order_id: int = 0  # specific position
    group_id: Optional[int] = None  # we'll fill this later


class Statping:
    def __init__(self, base_url, token):
        self.session = requests.Session()
        self.base_url = base_url  # https://localhost:12345
        self.session.headers = {"Authorization": f"Bearer {token}"}

    # Group actions
    def group_list(self):
        url = f"{self.base_url}/api/groups"
        response = self.session.get(url, json={})
        return response.json()

    def group_create(self, group_name, public=True):
        already_exists, group_id = self._group_exists(group_name)
        if already_exists:
            logging.info(f"[Create Group] '{group_name}' already exists with ID: {group_id}")
            return {'id': group_id}
        payload = {
            "name": group_name,
            "public": public
        }
        response = self.session.post(f"{self.base_url}/api/groups", json=payload)
        return response.json()

    def group_view(self, group_id):
        response = self.session.get(f"{self.base_url}/api/groups/{group_id}", json={})
        return response.json()

    def group_delete(self, group_id):
        response = self.session.delete(f"{self.base_url}/api/groups/{group_id}")
        return response.json()

    # Service actions
    def service_create(self, service: ServiceItem) -> bool:
        already_exists, service_id = self._service_exists(service.name)
        try:
            payload = asdict(service)
            if already_exists:
                logging.info(f"[Create Service] '{service.name}' already exists with ID: {service_id}. Replacing")
                self.service_update(service_id, payload)
                return True
            response = self.session.post(f"{self.base_url}/api/services", json=payload)
            if response.status_code == 200:
                logging.info(f"[Create Service] Created service: [{service.name}]")
                return True
            logging.error(f"[Create Service] Failed to create service: [{service.name}][{response.text}]")
        except TypeError:
            logging.error("[Create Service] ServiceItem conversion to dict failed. Did you instantiate and pass a ServiceItem?")
        logging.error(f"[Create Service] Failed to create service: [{service.name}]")
        return False

    def service_list(self):
        response = self.session.get(f"{self.base_url}/api/services")
        if response.status_code == 200:
            return response.json()
        return {}

    def service_update(self, service_id, service_body):
        if not service_id or not service_body:
            logging.error("[Update Service] service id or body was empty")
            return {}
        response = self.session.post(f"{self.base_url}/api/services/{service_id}", json=service_body)
        return response.json()

    def _service_exists(self, name: str) -> Tuple[bool, int]:
        services = self.service_list()
        for svc in services:
            if svc['name'] == name:
                return True, svc['id']
        return False, -1

    def _group_exists(self, name: str) -> Tuple[bool, int]:
        groups = self.group_list()
        for grp in groups:
            if grp['name'] == name:
                return True, grp['id']
        return False, 0


if __name__ == "__main__":
    token = environ.get("API_TOKEN", "4745ac0a5e8f6927cf98d4e3279fef3131dfd2156bb5ccc0d7610f07218652f3")
    host = environ.get("API_HOST", "http://localhost:8080")
    client = Statping(host, token)

    if len(argv) != 2:
        print("Usage: provision.py file.yaml")
        exit(1)
    input_file = argv[1]
    if not Path.is_file(Path(input_file)):
        logging.error("Did you pass a valid file?")
        print("Usage: provision.py file.yaml")
        exit(1)

    with open('status.yaml', 'r') as f:
        data = yaml.load(f, Loader=SafeLoader)

    for group in data:
        group_id = client.group_create(group.get('name'), group.get('public', True)).get('id')
        if not group_id:
            logging.error("Failed to extract group id")
            exit(1)
        if 'entries' not in group.keys():
            continue
        for host in group['entries']:
            host['group_id'] = group_id

            for field in fields(ServiceItem):
                if field.name not in host.keys():
                    host[field.name] = field.default
            host_serviceItem = ServiceItem(**host)
            logging.debug(host_serviceItem)
            service_id = client.service_create(host_serviceItem)
