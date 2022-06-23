import json
import uuid

import pytest
from rest_framework import status

from api.models import ShopUnit, ShopUnitStat

from api.tests.utils import generate_imports, generate_unit, CATEGORY,\
    OFFER, assert_400, deep_sort_children, print_diff, assert_404


DUPLICATE_IDS = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 79999
            },
            {
                "type": "CATEGORY",
                "name": "Xomiа Readme 10",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 59999
            }
        ],
        "updateDate": "2022-02-02T12:00:00Z"
    },
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            },
            {
                "type": "OFFER",
                "name": "jPhone 13",
                "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 79999
            },
            {
                "type": "OFFER",
                "name": "Xomiа Readme 10",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "price": 59999
            }
        ],
        "updateDate": "2022-02-02T12:00:00Z"
    }
]

WRONG_LAST = [
    {
        "items": [
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                "parentId": None,
            },
            {
                "type": "CATEGORY",
                "name": "Смартфоны",
                "id": "d515e43f-f3f6-4471-bb77-6b455017a2d3",
                "parentId": None,
                "price": 893  # invalid
            },
        ],
        "updateDate": "2022-02-02T12:00:00Z"
    },
]

EXPECTED_TREE = {
    "type": "CATEGORY",
    "name": "Товары",
    "id": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
    "price": 58599,
    "parentId": None,
    "date": "2022-02-03T15:00:00Z",
    "children": [
        {
            "type": "CATEGORY",
            "name": "Телевизоры",
            "id": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 50999,
            "date": "2022-02-03T15:00:00Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": "Samson 70\" LED UHD Smart",
                    "id": "98883e8f-0507-482f-bce2-2fb306cf6483",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 32999,
                    "date": "2022-02-03T12:00:00Z",
                    "children": None,
                },
                {
                    "type": "OFFER",
                    "name": "Phyllis 50\" LED UHD Smarter",
                    "id": "74b81fda-9cdc-4b63-8927-c978afed5cf4",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 49999,
                    "date": "2022-02-03T12:00:00Z",
                    "children": None
                },
                {
                    "type": "OFFER",
                    "name": "Goldstar 65\" LED UHD LOL Very Smart",
                    "id": "73bc3b36-02d1-4245-ab35-3106c9ee1c65",
                    "parentId": "1cc0129a-2bfe-474c-9ee6-d435bf5fc8f2",
                    "price": 69999,
                    "date": "2022-02-03T15:00:00Z",
                    "children": None
                }
            ]
        },
        {
            "type": "CATEGORY",
            "name": "Смартфоны",
            "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
            "parentId": "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1",
            "price": 69999,
            "date": "2022-02-02T12:00:00Z",
            "children": [
                {
                    "type": "OFFER",
                    "name": "jPhone 13",
                    "id": "863e1a7a-1304-42ae-943b-179184c077e3",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 79999,
                    "date": "2022-02-02T12:00:00Z",
                    "children": None
                },
                {
                    "type": "OFFER",
                    "name": "Xomiа Readme 10",
                    "id": "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4",
                    "parentId": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "price": 59999,
                    "date": "2022-02-02T12:00:00Z",
                    "children": None
                }
            ]
        },
    ]
}


ROOT_ID = "069cb8d7-bbdd-47d3-ad8f-82ef4c269df1"
LEAF_ID = "863e1a7a-1304-42ae-943b-179184c077e3"

pytestmark = pytest.mark.django_db


class TestImports:
    endpoint = '/imports'

    def test_float_price(self, db, api_client):
        imports = generate_imports([generate_unit(unit_type=OFFER, price=1.9)])

        response = api_client().post(
            self.endpoint,
            data=imports,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert ShopUnit.objects.count() == 1
        assert ShopUnitStat.objects.count() == 1

    def test_same_id_parent_id(self, db, api_client):
        unit_id = str(uuid.uuid4())
        imports = generate_imports([generate_unit(unit_type=OFFER, unit_id=unit_id, parent_id=unit_id)])

        response = api_client().post(
            self.endpoint,
            data=imports,
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0

    def test_trash(self, db, api_client):
        unit = {
            "items": [
                {
                    "type": "CATEGORY",
                    "name": "Смартфоны",
                    "parentId": None,
                },
            ],
            "updateDate": "2022-02-02T12:00:00Z",
        }

        response = api_client().post(
            self.endpoint,
            data=unit,
            format='json'
        )
        assert_400(response)
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0

        unit = {
            "items": "sadf",
            "updateDate": "2022-02-02T12:00:00Z",
        }

        response = api_client().post(
            self.endpoint,
            data=unit,
            format='json'
        )
        assert_400(response)
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0

        unit = {
            "items": [
                {
                    "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "type": "CATEGORY",
                    "parentId": None,
                },
            ],
            "updateDate": "2022-02-02T12:00:00Z",
        }

        response = api_client().post(
            self.endpoint,
            data=unit,
            format='json'
        )
        assert_400(response)
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0

    def test_correct_imports(self, api_client, correct_import):
        assert ShopUnit.objects.count() == 8
        assert ShopUnitStat.objects.count() == 11
        assert ShopUnitStat.objects.filter(shop_unit_id=ROOT_ID).count() == 3
        assert ShopUnitStat.objects.filter(shop_unit_id=LEAF_ID).count() == 1
        assert ShopUnitStat.objects.filter(shop_unit_id=ROOT_ID).last().price == 58599

    def test_duplicate_ids(self, db, api_client):
        for i, batch in enumerate(DUPLICATE_IDS):
            response = api_client().post(
                self.endpoint,
                data=batch,
                format='json'
            )
            assert_400(response)
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0

    def test_update_unit(self, db, api_client):
        unit = {
            "items": [
                {
                    "type": "CATEGORY",
                    "name": "Смартфоны",
                    "id": "d515e43f-f3f6-4471-bb77-6b455017a2d2",
                    "parentId": None,
                },
            ],
            "updateDate": "2022-02-02T12:00:00Z",
        }

        response = api_client().post(
            self.endpoint,
            data=unit,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert ShopUnit.objects.count() == 1
        assert ShopUnit.objects.get(id=unit['items'][0]['id']).name == unit['items'][0]['name']
        assert ShopUnitStat.objects.count() == 0

        unit['items'][0]['name'] = 'Планшеты'
        response = api_client().post(
            self.endpoint,
            data=unit,
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert ShopUnit.objects.count() == 1
        assert ShopUnit.objects.get(id=unit['items'][0]['id']).name == unit['items'][0]['name']
        assert ShopUnitStat.objects.count() == 0

    def test_change_offer_to_category(self, db, api_client):
        unit_id = str(uuid.uuid4())
        offer = generate_unit(unit_type=OFFER, unit_id=unit_id)
        category = generate_unit(unit_type=CATEGORY, unit_id=unit_id)
        OFFER_CATEGORY = [
            generate_imports([category]),
            generate_imports([offer]),
        ]

        for i, batch in enumerate(OFFER_CATEGORY):
            response = api_client().post(
                self.endpoint,
                data=batch,
                format='json'
            )
        assert_400(response)
        assert ShopUnit.objects.count() == 1
        ShopUnit.objects.all().delete()

        for i, batch in enumerate(reversed(OFFER_CATEGORY)):
            response = api_client().post(
                self.endpoint,
                data=batch,
                format='json'
            )
        assert_400(response)
        assert ShopUnit.objects.count() == 1

    def test_offer_as_parent(self, api_client):
        parent_unit = generate_unit(unit_type=OFFER)
        child_unit = generate_unit(parent_id=parent_unit['id'])
        OFFER_AS_PARENT = [
            generate_imports([parent_unit]),
            generate_imports([child_unit]),
        ]
        for i, batch in enumerate(OFFER_AS_PARENT):
            response = api_client().post(
                self.endpoint,
                data=batch,
                format='json'
            )
        assert_400(response)
        assert ShopUnit.objects.count() == 1
        assert ShopUnitStat.objects.count() == 1

    def test_wrong_price(self, api_client):
        priceless = generate_imports([generate_unit(unit_type=OFFER)])
        priceless['items'][0].pop('price')
        WRONG_PRICE = [
            generate_imports([generate_unit(unit_type=CATEGORY, price=1)]),
            priceless,
            generate_imports([generate_unit(unit_type=OFFER, price=-1)]),
        ]
        for i, batch in enumerate(WRONG_PRICE):
            response = api_client().post(
                self.endpoint,
                data=batch,
                format='json'
            )
            print(json.dumps(batch))
            assert_400(response)
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0

    def test_wrong_last(self, api_client):
        for i, batch in enumerate(WRONG_LAST):
            response = api_client().post(
                self.endpoint,
                data=batch,
                format='json'
            )

            assert_400(response)
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0


class TestNodes:

    endpoint = '/nodes'

    def test_root(self, api_client, correct_import):
        response = api_client().get(
            f'{self.endpoint}/{ROOT_ID}'
        )
        response = response.data
        deep_sort_children(response)
        deep_sort_children(EXPECTED_TREE)
        print('---------------------------')
        print_diff(EXPECTED_TREE, response)
        print('---------------------------')

        assert response == EXPECTED_TREE

    def test_all(self, api_client, correct_import):
        def find_subtree_by_id(tree, unit_id):
            if tree['id'] == unit_id:
                return tree
            if tree['children']:
                for child in tree['children']:
                    found = find_subtree_by_id(child, unit_id)
                    if found:
                        return found

        units = ShopUnit.objects.all()
        for unit in units:
            response = api_client().get(
                f'{self.endpoint}/{unit.id}'
            )
            assert response.status_code == status.HTTP_200_OK
            response = response.data
            tree = find_subtree_by_id(EXPECTED_TREE, unit.id)
            deep_sort_children(response)
            deep_sort_children(tree)
            print('---------------------------')
            print_diff(tree, response)
            print('---------------------------')

            assert response == tree

    def test_404(self, api_client):
        response = api_client().get(
            f'{self.endpoint}/069cb8d7-bbdd-47d3-ad8f-82ef4c269df1'
        )
        assert_404(response)

        response = api_client().get(
            f'{self.endpoint}/1'
        )
        assert_400(response)


class TestDelete:

    endpoint = '/delete'

    def test_leaf(self, api_client, correct_import):
        response = api_client().delete(
            f'{self.endpoint}/{LEAF_ID}'
        )

        assert response.status_code == status.HTTP_200_OK
        assert ShopUnit.objects.count() == 7
        assert ShopUnitStat.objects.filter(shop_unit_id=LEAF_ID).count() == 0
        assert ShopUnitStat.objects.all().count() == 10

    def test_root(self, api_client, correct_import):
        response = api_client().delete(
            f'{self.endpoint}/{ROOT_ID}'
        )
        assert response.status_code == status.HTTP_200_OK
        assert ShopUnit.objects.count() == 0
        assert ShopUnitStat.objects.count() == 0

        response = api_client().delete(
            f'{self.endpoint}/{ROOT_ID}'
        )
        assert_404(response)

        response = api_client().delete(
            f'{self.endpoint}/1'
        )
        assert_400(response)


class TestSales:

    endpoint = '/sales'

    def test_correct_imports(self, api_client, correct_import):
        date = '2022-02-01T12:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}?date={date}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 0

        date = '2022-02-02T12:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}?date={date}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 4

        date = '2022-02-03T13:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}?date={date}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 4

        date = '2022-02-03T15:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}?date={date}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 5
        assert len(response.data["items"]) == 5

        date = '2022-02-05T15:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}?date={date}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 0

    def test_wrong(self, api_client, correct_import):
        response = api_client().get(
            f'{self.endpoint}'
        )
        assert_400(response)

        date = '2022-02-01T12:00:00.0'
        response = api_client().get(
            f'{self.endpoint}?date={date}'
        )
        assert_400(response)


class TestStatistic:

    endpoint = '/node'

    def test_correct_imports(self, api_client, correct_import):
        response = api_client().get(
            f'{self.endpoint}/{ROOT_ID}/statistic'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 3

        date_start = '2022-02-01T12:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}/{ROOT_ID}/statistic?dateStart={date_start}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 3

        date_end = '2022-02-01T12:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}/{ROOT_ID}/statistic?dateEnd={date_end}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 0

        date_end = '2022-02-05T12:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}/{ROOT_ID}/statistic?dateEnd={date_end}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 3

        date_start = '2022-02-01T12:00:00.0Z'
        date_end = '2022-02-05T12:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}/{ROOT_ID}/statistic?dateEnd={date_end}&dateStart={date_start}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 3

        date_start = '2022-02-01T12:00:00.0Z'
        date_end = '2022-02-05T12:00:00.0Z'
        response = api_client().get(
            f'{self.endpoint}/{LEAF_ID}/statistic?dateEnd={date_end}&dateStart={date_start}'
        )
        assert response.status_code == 200
        assert len(response.data["items"]) == 1

    def test_changes(self, api_client, correct_import):
        UNIT_ID = "d155e43f-f3f6-4471-bb77-6b455017a2d2"
        unit = {
            "items": [
                {
                    "type": "OFFER",
                    "name": "Смартфон",
                    "id": UNIT_ID,
                    "parentId": None,
                    "price": 5
                },
            ],
            "updateDate": "2022-02-02T12:00:00Z",
        }

        api_client().post(
            "/imports",
            data=unit,
            format='json'
        )
        response = api_client().get(
            f'{self.endpoint}/{UNIT_ID}/statistic'
        )
        assert response.status_code == 200
        assert len(response.data) == 1

        unit["updateDate"] = "2022-02-03T13:00:00Z"
        unit["items"][0]["price"] = 7
        unit["items"][0]["name"] = 'Телефон'
        unit["items"][0]["parentId"] = ROOT_ID
        api_client().post(
            "/imports",
            data=unit,
            format='json'
        )
        response = api_client().get(
            f'{self.endpoint}/{UNIT_ID}/statistic'
        )

        assert response.status_code == 200
        assert len(response.data["items"]) == 2
        assert sum(item["price"] for item in response.data["items"]) == 12
        assert response.data["items"][0]["name"] == "Смартфон"
        assert response.data["items"][1]["name"] == "Телефон"
        assert response.data["items"][0]["parentId"] is None
        assert response.data["items"][1]["parentId"] == ROOT_ID
