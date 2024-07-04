from django.db.models import TextChoices
from rest_framework import serializers as sz


class TravelDecisionEnum(TextChoices):
    YES = "Can Visit"
    NO = "Shouldn't visit"


class TravelDecisionInSerializer(sz.Serializer):
    current_district_id = sz.IntegerField(required=True)
    dest_district_id = sz.IntegerField(required=True)
    travel_date = sz.DateField(required=True)


class TravelDecisionOutSerializer(sz.Serializer):
    travel_date = sz.DateField()
    decisition = sz.ChoiceField(choices=TravelDecisionEnum.choices)
