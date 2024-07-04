from django.urls import path

from . import views

urlpatterns = [
    path(
        "top-districts/", view=views.TopDistrictListView.as_view(), name="top-districts"
    )
]
