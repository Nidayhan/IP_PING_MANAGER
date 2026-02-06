from django import forms
from .models import IPAddress


class IPAddressForm(forms.ModelForm):
    class Meta:
        model = IPAddress
        fields = ['ip_address', 'backbone', 'device', 'ssid', 'mac', 'seri_no', 'status', 'location', 'alt_router']
        widgets = {
            'status': forms.RadioSelect(choices=[('Boşta', 'Boşta'), ('Kullanımda', 'Kullanımda')]),
        }

class IPCalculatorForm(forms.Form):
    ip_address = forms.GenericIPAddressField(protocol='IPv4', required=True)
    subnet = forms.IntegerField(min_value=0, max_value=32, required=True)