from django.urls import path
from api.views import ImportsView, NodesList, InvalidIdGet,\
    InvalidIdDelete, NodesDestroy, SalesView, StatisticsView

urlpatterns = [
    path('imports', ImportsView.as_view()),
    path('nodes/<uuid:id>', NodesList.as_view()),
    path('nodes/<str:id>', InvalidIdGet.as_view()),
    path('node/<uuid:id>/statistic', StatisticsView.as_view()),
    path('node/<str:id>/statistic', InvalidIdGet.as_view()),
    path('delete/<uuid:id>', NodesDestroy.as_view()),
    path('delete/<str:id>', InvalidIdDelete.as_view()),
    path('sales', SalesView.as_view()),
]
