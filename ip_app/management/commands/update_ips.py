from django.core.management.base import BaseCommand
from ip_app.models import IPAddress


class Command(BaseCommand):
    help = 'Güncellenmiş IP adreslerini kontrol et ve güncelle'

    def handle(self, *args, **kwargs):
        ips = IPAddress.objects.all()
        for ip in ips:
            # Burada ping ve success alanlarını güncelleyin
            ip.ping = False  # veya diğer uygun değer
            ip.success = False  # veya diğer uygun değer
            ip.save()
            self.stdout.write(self.style.SUCCESS(f'{ip.ip_address} güncellendi'))
