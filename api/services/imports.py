from typing import List, Dict

from api.models import OFFER, ShopUnit
from api.serializers import ValidationErrorException, ShopUnitSerializer
from rest_framework.exceptions import APIException
from rest_framework.serializers import Serializer


def item_pre_validation(item: Dict) -> None:
    """Проверяет наличие обязательных полей"""
    try:
        assert 'id' in item
        assert 'name' in item
        assert 'type' in item
    except AssertionError:
        raise ValidationErrorException()


def delete_added(ids: List) -> None:
    """Удаляет элементы магазина по id"""
    ShopUnit.objects.filter(id__in=ids).delete()


def terminate(unit_ids_added) -> None:
    """Удалеят добавленные элементы и возвращает пользователю 400"""
    delete_added(unit_ids_added)
    raise ValidationErrorException()


def add_items(items: List, update_date: str) -> None:
    """Обрабатывает добавление новых товаров и категорий"""
    items_serializers = {}
    unit_ids_added = []

    for item in items:
        item_pre_validation(item)
        serializer = ShopUnitSerializer(data=item)

        if item['id'] in items_serializers:
            raise ValidationErrorException()
        if 'parentId' in item and item['id'] == item['parentId']:
            raise ValidationErrorException()
        items_serializers[item['id']] = serializer

    def add_item_to_db(serializer: Serializer, items_serializers: Dict[str, Serializer]):
        try:
            is_valid = serializer.is_valid()
        except APIException:
            terminate(unit_ids_added)

        if is_valid:
            additional_params = {'date': update_date}
            if serializer.validated_data['type'] == OFFER:
                additional_params['weight'] = 1
            serializer.save(**additional_params)
            unit_ids_added.append(serializer.validated_data['id'])

            items_serializers.pop(str(serializer.validated_data['id']))
            return True
        elif 'parentId' in serializer.errors:
            try:
                return add_item_to_db(
                    items_serializers[serializer.data['parentId']], items_serializers)
            except KeyError:
                terminate(unit_ids_added)
        else:
            terminate(unit_ids_added)

    while len(items_serializers) > 0:
        add_item_to_db(items_serializers[list(items_serializers.keys())[0]], items_serializers)
