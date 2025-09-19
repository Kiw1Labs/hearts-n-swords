from rest_framework import serializers
from .models import Run, EventLog, Roll

class RunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Run
        fields = "__all__"

class EventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = "__all__"

class RollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roll
        fields = "__all__"
