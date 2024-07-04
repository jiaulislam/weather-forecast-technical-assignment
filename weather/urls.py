from django.urls import path

from . import views

urlpatterns = [
    path(
        "top-districts/", view=views.TopDistrictListView.as_view(), name="top-districts"
    ),
    path(
        "travel-decision/",
        view=views.TravelDecisionView.as_view(),
        name="travel-decision",
    ),
]
