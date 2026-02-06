from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class AltRouterOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class DeviceOption(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name

class LocationOption(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class BackboneOption(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class IPAddress(models.Model):
    
    subnet = models.CharField(max_length=18, blank=True, null=True)
    
    ip_address = models.GenericIPAddressField(unique=True)
    backbone = models.ForeignKey('BackboneOption', on_delete=models.SET_NULL, null=True, blank=True)
    device = models.ForeignKey('DeviceOption', on_delete=models.SET_NULL, null=True, blank=True)
    ssid = models.CharField(max_length=100, blank=True, null=True)
    mac = models.CharField(max_length=100, blank=True, null=True)
    seri_no = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('Boşta', 'Boşta'), ('Kullanımda', 'Kullanımda')],
        default='Boşta'
    )
    location = models.ForeignKey('LocationOption', on_delete=models.SET_NULL, null=True, blank=True)
    alt_router = models.ForeignKey('AltRouterOption', on_delete=models.SET_NULL, null=True, blank=True)
    ping = models.BooleanField(default=False)
    success = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    username = models.CharField(max_length=100, blank=True, null=True)
    sifre = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    public_ip = models.CharField(max_length=100, blank=True, null=True)
    device_name = models.CharField(max_length=100, blank=True, null=True)
    açıklama = models.CharField(max_length=18, blank=True, null=True)
    
    class Meta:
        permissions = [
            ("view_password","Can view passwords"),
            ("can_delete_subnet", "Can delete subnet"),
        ]
    
    
    def __str__(self):
        return f'{self.ip_address} - {"Success" if self.success else "Failure"}'
