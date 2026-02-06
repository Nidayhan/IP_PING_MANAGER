from django.test import TestCase
from ip_app.models import IPAddress
from django.urls import reverse
import json

class PingResultTestCase(TestCase):
    def setUp(self):
        # Test için birden fazla IP adresi oluşturun
        IPAddress.objects.create(ip_address='192.168.1.1', success=False, location='Old Location 1', route='Old Route 1')
        IPAddress.objects.create(ip_address='192.168.1.2', success=False, location='Old Location 2', route='Old Route 2')
        IPAddress.objects.create(ip_address='192.168.1.3', success=False, location='Old Location 3', route='Old Route 3')

    def test_save_ping_result(self):
        # Güncellenmiş verileri gönderin
        response = self.client.post(reverse('save_ping_result'), 
            content_type='application/json',
            data=json.dumps({
                'updates': [
                    {'ip_address': '192.168.1.1', 'success': True, 'location': 'New Location 1', 'route': 'New Route 1'},
                    {'ip_address': '192.168.1.2', 'success': True, 'location': 'New Location 2', 'route': 'New Route 2'},
                    {'ip_address': '192.168.1.3', 'success': True, 'location': 'New Location 3', 'route': 'New Route 3'}
                ]
            })
        )
        self.assertEqual(response.status_code, 200)
        
        # Veritabanında IP adreslerini kontrol edin
        ip1 = IPAddress.objects.get(ip_address='192.168.1.1')
        self.assertTrue(ip1.success)
        self.assertEqual(ip1.location, 'New Location 1')
        self.assertEqual(ip1.route, 'New Route 1')
        
        ip2 = IPAddress.objects.get(ip_address='192.168.1.2')
        self.assertTrue(ip2.success)
        self.assertEqual(ip2.location, 'New Location 2')
        self.assertEqual(ip2.route, 'New Route 2')
        
        ip3 = IPAddress.objects.get(ip_address='192.168.1.3')
        self.assertTrue(ip3.success)
        self.assertEqual(ip3.location, 'New Location 3')
        self.assertEqual(ip3.route, 'New Route 3')
