from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from .models import TrackerData, TrackerSession
import json


class TrackerDataModelTest(TestCase):
    def setUp(self):
        self.tracker_data = TrackerData.objects.create(
            deviceId="test-device-123",
            latitude=40.7128,
            longitude=-74.0060,
            speed=25.5,
            batteryLevel=85
        )

    def test_tracker_data_creation(self):
        self.assertEqual(self.tracker_data.deviceId, "test-device-123")
        self.assertEqual(self.tracker_data.latitude, 40.7128)
        self.assertEqual(self.tracker_data.speed, 25.5)
        self.assertEqual(self.tracker_data.batteryLevel, 85)

    def test_tracker_data_str(self):
        expected = f"TrackerData {self.tracker_data.deviceId} - {self.tracker_data.timestamp}"
        self.assertEqual(str(self.tracker_data), expected)


class TrackerSessionModelTest(TestCase):
    def setUp(self):
        self.session = TrackerSession.objects.create(
            sessionId="session-123",
            deviceId="test-device-123"
        )

    def test_tracker_session_creation(self):
        self.assertEqual(self.session.sessionId, "session-123")
        self.assertEqual(self.session.deviceId, "test-device-123")
        self.assertTrue(self.session.isActive)

    def test_tracker_session_str(self):
        expected = f"Session {self.session.sessionId} - {self.session.deviceId}"
        self.assertEqual(str(self.session), expected)


class TrackerDataAPITest(APITestCase):
    def test_post_tracker_data_success(self):
        data = {
            'deviceId': 'test-device-123',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'speed': 25.5,
            'batteryLevel': 85
        }
        
        response = self.client.post('/api/tracker/data/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Tracker data received successfully')

    def test_post_tracker_data_missing_device_id(self):
        data = {
            'latitude': 40.7128,
            'longitude': -74.0060
        }
        
        response = self.client.post('/api/tracker/data/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('deviceId is required', response.data['error'])

    def test_start_tracking_session(self):
        data = {
            'deviceId': 'test-device-123'
        }
        
        response = self.client.post('/api/tracker/session/start/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('sessionId', response.data)

    def test_end_tracking_session(self):
        # First create a session
        session = TrackerSession.objects.create(
            sessionId="test-session-123",
            deviceId="test-device-123"
        )
        
        data = {
            'sessionId': 'test-session-123'
        }
        
        response = self.client.post('/api/tracker/session/end/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_get_tracker_data(self):
        # Create some test data
        TrackerData.objects.create(
            deviceId="test-device-123",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        response = self.client.get('/api/tracker/data/?deviceId=test-device-123')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(len(response.data['data']), 1)
