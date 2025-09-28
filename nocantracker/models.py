from django.db import models
from django.utils import timezone


class TrackerData(models.Model):
    """
    Model to store tracker data posted from the app
    """
    deviceId = models.CharField(max_length=255, help_text="Unique device identifier")
    timestamp = models.DateTimeField(default=timezone.now, help_text="When the data was recorded")
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True, help_text="GPS latitude")
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True, help_text="GPS longitude")
    altitude = models.FloatField(null=True, blank=True, help_text="Altitude in meters")
    speed = models.FloatField(null=True, blank=True, help_text="Speed in km/h")
    heading = models.FloatField(null=True, blank=True, help_text="Direction in degrees")
    accuracy = models.FloatField(null=True, blank=True, help_text="GPS accuracy in meters")
    batteryLevel = models.IntegerField(null=True, blank=True, help_text="Battery percentage")
    networkType = models.CharField(max_length=50, null=True, blank=True, help_text="Network connection type")
    appVersion = models.CharField(max_length=20, null=True, blank=True, help_text="App version")
    additionalData = models.JSONField(null=True, blank=True, help_text="Additional custom data")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nocantracker_data'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['deviceId', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"TrackerData {self.deviceId} - {self.timestamp}"


class TrackerSession(models.Model):
    """
    Model to track tracking sessions
    """
    sessionId = models.CharField(max_length=255, unique=True, help_text="Unique session identifier")
    deviceId = models.CharField(max_length=255, help_text="Device identifier")
    startTime = models.DateTimeField(default=timezone.now, help_text="Session start time")
    endTime = models.DateTimeField(null=True, blank=True, help_text="Session end time")
    isActive = models.BooleanField(default=True, help_text="Whether session is currently active")
    totalDistance = models.FloatField(default=0.0, help_text="Total distance tracked in meters")
    dataPoints = models.IntegerField(default=0, help_text="Number of data points in this session")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nocantracker_sessions'
        ordering = ['-startTime']
        indexes = [
            models.Index(fields=['deviceId', 'startTime']),
            models.Index(fields=['sessionId']),
        ]

    def __str__(self):
        return f"Session {self.sessionId} - {self.deviceId}"
