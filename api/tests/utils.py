from typing import Optional, Dict, Any, List
from random import randint, choice
from datetime import datetime
import subprocess
import uuid
import json

from django.http import JsonResponse
import faker


MAX_INTEGER = 2147483647
fake = faker.Faker('ru_RU')
OFFER = "OFFER"
CATEGORY = "CATEGORY"


def generate_unit(
        parents_list: List = None,
        unit_id: Optional[str] = None,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
        unit_type: Optional[str] = None,
        price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Создает и возвращает unit магазина, автоматически генерируя данные для не
    указанных полей.
    """
    types = [OFFER, CATEGORY]
    if unit_id is None:
        unit_id = str(uuid.uuid4())

    if name is None:
        name = fake.name()

    if parent_id is None:
        if parents_list:
            parent_id = choice(parents_list)
        else:
            parent_id = None

    if unit_type is None:
        unit_type = choice(types)

    if unit_type == OFFER:
        if price is None:
            price = randint(0, MAX_INTEGER)
    else:
        if parents_list is not None:
            parents_list.append(unit_id)

    return {
        'id': unit_id,
        'name': name,
        'parentId': parent_id,
        'type': unit_type,
        'price': price,
    }


def generate_imports(
        item_list: List,
        import_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Создаеи и возвращает выгрузку unit'ов магазина для '/imports'
    """
    if import_date is None:
        import_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%zZ')

    return {
        "items": item_list,
        'updateDate': import_date
    }


def deep_sort_children(node):
    if node.get("children"):
        node["children"].sort(key=lambda x: x["id"])

        for child in node["children"]:
            deep_sort_children(child)


def print_diff(expected, response):
    with open("expected.json", "w") as f:
        json.dump(expected, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    with open("response.json", "w") as f:
        json.dump(response, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    subprocess.run(["git", "--no-pager", "diff", "--no-index",
                    "expected.json", "response.json"])


def assert_400(response):
    # print(response.data)
    assert response.status_code == 400
    assert response.data['code'] == 400
    assert response.data['message'] == 'Validation Failed'


def assert_404(response):
    assert response.status_code == 404
    if isinstance(response, JsonResponse):
        assert response.json()['code'] == 404
        assert response.json()['message'] == 'Item not found'
    else:
        assert response.data['code'] == 404
        assert response.data['message'] == 'Item not found'
