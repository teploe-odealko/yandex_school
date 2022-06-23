from rest_framework import status
from rest_framework.generics import DestroyAPIView, ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import ShopUnit, ShopUnitStat
from api.serializers import ShopUnitSerializer, ValidationErrorException, ShopUnitStatSerializer

from api.services.imports import add_items
from api.services.sales import get_sales_before_24h
from api.services.statistics import get_unit_statistics


class ImportsView(APIView):
    """ Обработка get '/imports' """

    def post(self, request):
        items = request.data['items']
        update_date = request.data['updateDate']
        if update_date is None or items is None:
            raise ValidationErrorException()

        add_items(items, update_date)

        return Response(
            status=status.HTTP_200_OK
        )


class NodesList(RetrieveAPIView):
    """ Обработка get '/nodes/{uuid}' """
    serializer_class = ShopUnitSerializer
    lookup_field = 'id'

    def get_queryset(self):
        query = ShopUnit.objects.all()
        return query


class InvalidIdGet(APIView):
    """ Обработка get '/nodes/{not uuid}' """

    def get(self, request, id):
        raise ValidationErrorException()


class InvalidIdDelete(APIView):
    """ Обработка delete '/delete/{not uuid}' """

    def delete(self, request, id):
        raise ValidationErrorException()


class NodesDestroy(DestroyAPIView):
    """ Обработка delete '/delete/{uuid}' """
    serializer_class = ShopUnitSerializer
    lookup_field = 'id'

    def get_queryset(self):
        query = ShopUnit.objects.all()
        return query

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        ShopUnitStat.objects.filter(shop_unit_id=instance.id).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_200_OK)


class SalesView(ListAPIView):
    """ Обработка get '/sales' """
    serializer_class = ShopUnitStatSerializer

    def get_queryset(self):
        date_param = self.request.query_params.get('date')
        if not date_param:
            raise ValidationErrorException()

        queryset = get_sales_before_24h(date_param)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"items": serializer.data})


class StatisticsView(APIView):
    """ Обработка get '/node/{id}/statistics' """

    def get(self, request, id):

        date_start = request.query_params.get('dateStart')
        date_end = request.query_params.get('dateEnd')

        queryset = get_unit_statistics(
            id, date_start=date_start, date_end=date_end)

        return Response(
            {"items": ShopUnitStatSerializer(queryset, many=True).data})
