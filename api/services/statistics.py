from datetime import datetime
from uuid import UUID

from api.models import ShopUnitStat
from api.serializers import ValidationErrorException
from django.db.models import QuerySet


def get_unit_statistics(id: UUID, date_start: str = None, date_end: str = None) -> QuerySet:
    """ Статистика за по элементу магазина за определенное время """
    filter_params = {}

    if date_start:
        try:
            date_start = datetime.strptime(
                date_start, '%Y-%m-%dT%H:%M:%S.%f%z'
            )
            filter_params['date__gte'] = date_start
        except ValueError:
            raise ValidationErrorException()

    if date_end:
        try:
            date_end = datetime.strptime(
                date_end, '%Y-%m-%dT%H:%M:%S.%f%z'
            )
            filter_params['date__lte'] = date_end
        except ValueError:
            raise ValidationErrorException()

    query = ShopUnitStat.objects.filter(shop_unit_id=id, **filter_params)
    return query
