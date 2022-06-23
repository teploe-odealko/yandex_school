from rest_framework import serializers, status
from rest_framework.exceptions import APIException

from .models import ShopUnit, ShopUnitStat, CATEGORY
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # response = {}
    # Now add the HTTP status code to the response.
    response_data = {}
    if response is not None:
        response_data['code'] = response.status_code
        if response_data['code'] == 400:
            response_data['message'] = "Validation Failed"
        elif response_data['code'] == 404:
            response_data['message'] = "Item not found"
    try:
        response.data = response_data
    except AttributeError:
        pass
    return response


class ValidationErrorException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Validation Failed'


class TypeChangingException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Type changing is forbidden'


class WrongPriceException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Price of category must be null; price of offer must not be null'


class ParentIsCategoryException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Type of parent must be a category'


class ShopUnitStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnitStat
        fields = ('id', 'name', 'date', 'parentId', 'price', 'type')

    id = serializers.CharField(source='shop_unit_id.id')
    type = serializers.CharField(source='shop_unit_id.type')
    parentId = serializers.CharField(source='parent')


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class ShopUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopUnit
        fields = ('type', 'name', 'id',  'price', 'parentId', 'date', 'children')

    price = serializers.FloatField(allow_null=True, required=False)
    date = serializers.DateTimeField(allow_null=True, read_only=True)
    id = serializers.UUIDField()
    children = RecursiveField(many=True, allow_null=True, read_only=True)
    parentId = serializers.PrimaryKeyRelatedField(
        source='parent',
        queryset=ShopUnit.objects.all(),
        allow_null=True,
    )

    def to_representation(self, data):
        data = super(ShopUnitSerializer, self).to_representation(data)
        if len(data['children']) == 0:
            data['children'] = None
        if data['price']:
            data['price'] = int(data['price'])
        return data

    def validate(self, attrs):
        try:
            instance = ShopUnit.objects.get(id=attrs['id'])
            if instance.type != attrs['type']:
                raise TypeChangingException()
        except ShopUnit.DoesNotExist:
            pass

        if attrs['type'] == CATEGORY:
            if 'price' in attrs and attrs['price'] is not None:
                raise WrongPriceException()
        else:
            if 'price' not in attrs or attrs['price'] is None:
                raise WrongPriceException()

        return attrs

    def validate_parentId(self, value):
        if value:
            if value.type == CATEGORY:
                return value
            raise ParentIsCategoryException()

    def validate_price(self, value):
        if value and value < 0:
            raise ValidationErrorException()
        if value:
            return int(value)
        return value

    def create(self, validated_data):
        shop_unit, created = ShopUnit.objects.update_or_create(
            id=validated_data['id'], defaults=validated_data)
        return shop_unit
