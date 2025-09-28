from django.contrib import admin
from .models import TrackerData, TrackerSession


@admin.register(TrackerData)
class TrackerDataAdmin(admin.ModelAdmin):
    list_display = ['deviceId', 'timestamp', 'latitude', 'longitude', 'speed', 'batteryLevel']
    list_filter = ['deviceId', 'timestamp', 'networkType']
    search_fields = ['deviceId', 'appVersion']
    readonly_fields = ['createdAt', 'updatedAt']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Device Info', {
            'fields': ('deviceId', 'timestamp', 'appVersion')
        }),
        ('Location Data', {
            'fields': ('latitude', 'longitude', 'altitude', 'accuracy')
        }),
        ('Movement Data', {
            'fields': ('speed', 'heading')
        }),
        ('Device Status', {
            'fields': ('batteryLevel', 'networkType')
        }),
        ('Additional Data', {
            'fields': ('additionalData',)
        }),
        ('Timestamps', {
            'fields': ('createdAt', 'updatedAt'),
            'classes': ('collapse',)
        })
    )


@admin.register(TrackerSession)
class TrackerSessionAdmin(admin.ModelAdmin):
    list_display = ['sessionId', 'deviceId', 'startTime', 'endTime', 'isActive', 'dataPoints', 'totalDistance']
    list_filter = ['deviceId', 'isActive', 'startTime']
    search_fields = ['sessionId', 'deviceId']
    readonly_fields = ['createdAt', 'updatedAt']
    ordering = ['-startTime']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('sessionId', 'deviceId', 'isActive')
        }),
        ('Timing', {
            'fields': ('startTime', 'endTime')
        }),
        ('Statistics', {
            'fields': ('totalDistance', 'dataPoints')
        }),
        ('Timestamps', {
            'fields': ('createdAt', 'updatedAt'),
            'classes': ('collapse',)
        })
    )
