import datetime
import logging
import random
import string
import uuid

from rest_framework import status
from locust import HttpUser, constant, task
from locust.exception import RescheduleTask

from yandex.api.tests.utils import generate_unit

OFFER = "OFFER"
CATEGORY = "CATEGORY"


def generate_imports(num_imports=1):
    parent_ids = [None]
    final_imports = []
    base_time = datetime.datetime.now()
    for n in range(num_imports):
        single_import = {}
        base_time += datetime.timedelta(minutes=5)
        single_import['updateDate'] = base_time.strftime('%Y-%m-%dT%H:%M:%S.%f%zZ')
        # print("single_import['updateDate']", single_import['updateDate'])
        single_import['items'] = [generate_unit(parent_ids)]
        final_imports.append(single_import)
    return final_imports


class WebsiteUser(HttpUser):
    wait_time = constant(1)

    def make_dataset(self):
        return generate_imports()

    def request(self, method, path, expected_status, **kwargs):
        with self.client.request(
                method, path, catch_response=True, **kwargs
        ) as resp:
            if resp.status_code != expected_status:
                resp.failure(f'expected status {expected_status}, '
                             f'got {resp.status_code}')
            logging.info(
                '%s %s, http status %d (expected %d), took %rs',
                method, path, resp.status_code, expected_status,
                resp.elapsed.total_seconds()
            )
            return resp

    def create_import(self, dataset):
        for single_import in dataset:
            resp = self.request('POST', '/imports', status.HTTP_200_OK,
                                json=single_import)
            if resp.status_code != status.HTTP_200_OK:
                raise RescheduleTask

    def nodes(self, unit_id):
        self.request('GET', f'/nodes/{unit_id}', status.HTTP_200_OK, name='/nodes/')

    def statistic(self, unit_id):
        self.request('GET', f'/node/{unit_id}/statistic', status.HTTP_200_OK, name='/statistic/')

    def sales(self, update_date):
        self.request('GET', f'/sales?date={update_date}', status.HTTP_200_OK, name='/sales/')

    @task(1)
    def workflow(self):
        # self.round += 1
        dataset = self.make_dataset()

        self.create_import(dataset)
        self.nodes(dataset[0]['items'][0]['id'])
        self.statistic(dataset[0]['items'][0]['id'])



