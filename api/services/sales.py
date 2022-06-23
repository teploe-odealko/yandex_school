from datetime import datetime, timedelta

from api.models import ShopUnitStat
from api.serializers import ValidationErrorException
from django.db.models import QuerySet


def get_sales_before_24h(end_date: str) -> QuerySet:
    """Продажи товаров за последние 24 часа от даты"""
    try:
        end_date = datetime.strptime(
            end_date, '%Y-%m-%dT%H:%M:%S.%f%z'
        )
    except ValueError:
        raise ValidationErrorException()
    start_date = end_date - timedelta(days=1)
    return ShopUnitStat.objects \
        .order_by('shop_unit_id', '-date') \
        .filter(date__range=(start_date, end_date)) \
        .distinct('shop_unit_id')
