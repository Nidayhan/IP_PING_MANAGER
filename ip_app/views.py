from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import subprocess
from .models import IPAddress
from .forms import IPAddressForm, IPCalculatorForm
from django.db.models import Q
import ipaddress

def ip_calculator_view(request):
    if request.method == 'POST':
        form = IPCalculatorForm(request.POST)
        if form.is_valid():
            ip_address = form.cleaned_data['ip_address']
            subnet = form.cleaned_data['subnet']
            results = calculate_ip_range(ip_address, subnet)
            
            # JSON yanıtı döndür
            return JsonResponse(results)
        else:
            # Form geçersizse
            return JsonResponse({'error': 'Invalid form data'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
def calculate_ip_range(ip_address, subnet):
    try:
        network = ipaddress.ip_network(f'{ip_address}/{subnet}', strict=False)

        # IP adresleri listesi oluşturuluyor
        ip_list = [str(ip) for ip in network.hosts()]

        # Bilgiler hesaplanıyor
        total_ips = len(ip_list)
        subnet_address = str(network.network_address)
        gateway_address = str(network.network_address + 1) if total_ips > 0 else 'N/A'

        return {
            'calculated_ips': ip_list,
            'total_ips': total_ips,
            'subnet_address': subnet_address,
            'gateway_address': gateway_address
        }
    except ValueError as e:
        print(f"Error calculating IP range: {e}")
        return {
            'calculated_ips': [],
            'total_ips': 'N/A',
            'subnet_address': 'N/A',
            'gateway_address': 'N/A'
        }

def ip_list_view(request):
    search_query = request.GET.get('search', '')
    if search_query:
        ip_addresses = IPAddress.objects.filter(
            Q(ip_address__icontains=search_query) |
            Q(backbone__name__icontains=search_query) |  
            Q(device__name__icontains=search_query) |  
            Q(ssid__icontains=search_query) |
            Q(mac__icontains=search_query) |
            Q(seri_no__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(location__name__icontains=search_query) |  
            Q(alt_router__name__icontains=search_query)  
        )
    else:
        ip_addresses = IPAddress.objects.all()
    
    return render(request, 'index.html', {'ip_addresses': ip_addresses})

def search_results(request):
    search_query = request.GET.get('search', '')
    if search_query:
        ip_addresses = IPAddress.objects.filter(
            Q(ip_address__icontains=search_query) |
            Q(backbone__name__icontains=search_query) |  
            Q(device__name__icontains=search_query) | 
            Q(ssid__icontains=search_query) |
            Q(mac__icontains=search_query) |
            Q(seri_no__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(location__name__icontains=search_query) |  
            Q(alt_router__name__icontains=search_query) 
        )
    else:
        ip_addresses = IPAddress.objects.all()
    
    return render(request, 'index.html', {'ip_addresses': ip_addresses})

def perform_ping_test(ip_address):
    """IP adresine ping testi yapar ve sonucunu döner."""
    try:
        output = subprocess.check_output(['ping', '-n', '1', ip_address], universal_newlines=True)
        if '1 packets transmitted, 1 received' in output or 'Reply from' in output:
            return True
        return False
    except subprocess.CalledProcessError:
        return False

@require_POST
def ping_ip(request):
            import json
            data = json.loads(request.body)
            ips = data.get('ips', [])
           
            results = {}
            for ip in ips:
                
                success = perform_ping_test(ip)  
                results[ip] = 'Başarılı' if success else 'Başarısız'

            return JsonResponse({'result': results})
       


@require_POST
def update_ip_status(request):
    """IP adresinin durumunu günceller ve ping testini yapar."""
    if request.method == 'POST':
        form = IPAddressForm(request.POST)
        if form.is_valid():
            ip_address = form.cleaned_data['ip_address']
            status = form.cleaned_data['status']
            location = form.cleaned_data['location']
            route = form.cleaned_data['route']
            
            ip, created = IPAddress.objects.get_or_create(ip_address=ip_address)
            ip.status = status
            ip.location = location
            ip.route = route
            
            ip.ping = perform_ping_test(ip_address)
            ip.success = ip.ping  # Başarı durumunu ping sonucuna göre belirle
            
            ip.save()

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    else:
        form = IPAddressForm()
    
    return render(request, 'your_template.html', {'form': form})

@require_POST
def check_ip_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ips = data.get('ips', [])

            results = {}
            for ip in ips:
                
                try:
                    result = subprocess.run(['ping', '-n', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if result.returncode == 0:
                        results[ip] = 'Başarılı'
                    else:
                        results[ip] = 'Başarısız'
                except Exception as e:
                    results[ip] = 'Hata'

            return JsonResponse({'results': results})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)