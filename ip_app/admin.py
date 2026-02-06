

from django.contrib import admin
from .models import IPAddress, BackboneOption, LocationOption, DeviceOption, AltRouterOption
from .forms import IPAddressForm
from django.http import HttpResponseRedirect
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django import forms
from ipaddress import ip_network, AddressValueError, NetmaskValueError
from django.db import IntegrityError
from .views import ping_ip
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied



class AltRouterOptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(AltRouterOption, AltRouterOptionAdmin)

class DeviceOptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(DeviceOption, DeviceOptionAdmin)

class LocationOptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
admin.site.register(LocationOption, LocationOptionAdmin)

class BackboneOptionAdmin(admin.ModelAdmin):
    list_display =('name',)
admin.site.register(BackboneOption, BackboneOptionAdmin)

class IPRangeForm(forms.Form):
    ip_address = forms.CharField(label='IP Address', max_length=18)
    subnet = forms.CharField(label='Subnet', max_length=18, required=False)
    device_name = forms.CharField(label='Device Name', max_length=100, required=False)
    status = forms.ChoiceField(label='Status', choices=[('Kullanımda', 'Kullanımda'), ('Boşta', 'Boşta')], required=False)
    backbone = forms.ModelChoiceField(label='Backbone', queryset=BackboneOption.objects.all(), required=False)
    alt_router = forms.ModelChoiceField(label='Alt Router', queryset=AltRouterOption.objects.all(), required=False)
    ssid = forms.CharField(label='SSID', max_length=100, required=False)
    device = forms.CharField(label='Device', max_length=100, required=False)
    seri_no = forms.CharField(label='Serial No', max_length=100, required=False)
    mac = forms.CharField(label='MAC Address', max_length=17, required=False)
    açıklama = forms.CharField(label='MAC Address', max_length=17, required=False)
    
class IPAddressAdmin(admin.ModelAdmin):
    
    change_form_template = 'admin/ipCalculator_change_form.html'  # Özel şablon yolu

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('calculate/', self.admin_site.admin_view(self.calculate_ip_view), name='ip_calculator'),
        ]
        return custom_urls + urls

    def calculate_ip_view(self, request):
        
        return HttpResponseRedirect('/ip-calculator/') 

    def response_change(self, request, obj):
        if "_open_calculator" in request.POST:
            
            return HttpResponseRedirect('/ip-calculator/')
        return super().response_change(request, obj)
    
    list_display = (
        'status', 'ping_button', 'ip_link', 'public_ip_link','device_name',
        'location', 'backbone', 'alt_router', 'ssid', 'device', 'seri_no', 'mac', 'username', 'display_alan_10','açıklama', 'edit_link'
    )
    list_filter = (
        'status', 'location',
        'backbone', 'device', 'alt_router',
    )
    search_fields = (
        'ip_address', 'subnet', 'username', 'sifre',
    )
    list_per_page = 50
    
    exclude = ('ping', 'success') 
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'ip_address', 'public_ip', 'subnet', 'username', 'sifre',
        'status','device_name', 'location', 'backbone', 'alt_router', 'ssid', 
        'device', 'seri_no', 'mac','açıklama', 'created_at', 'updated_at',
    )
    actions = ['mark_as_in_use','mark_as_free','select_all','delete_subnet']
    
    def get_form(self, request, obj=None, **kwargs):
        # Öncelikle formu al
        form = super().get_form(request, obj, **kwargs)
        
       
        if not request.user.has_perm('ip_app.view_password'):
            # Formun widget'larını güncelle
            # 'username' ve 'sifre' alanlarını formdan kaldır
            form.base_fields['username'].widget = forms.HiddenInput()
            form.base_fields['sifre'].widget = forms.HiddenInput()
        
        return form
    
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        
        # Kullanıcının `delete_subnet_permission` iznine sahip olup olmadığını kontrol eder
        if not request.user.has_perm('ip_app.delete_subnet_permission'):
            actions.pop('delete_subnet', None)
        
        return actions
    
    def mark_as_in_use(self, request, queryset):
        queryset.update(status='Kullanımda')
        self.message_user(request, "Seçilen IP'ler kullanımda olarak işaretlendi.")
    mark_as_in_use.short_description = "Seçilen IP'leri Kullanımda olarak işaretle"

    def mark_as_free(self, request, queryset):
        queryset.update(status='Boşta')
        self.message_user(request, "Seçilen IP'ler boşta olarak işaretlendi.")
    mark_as_free.short_description = "Seçilen IP'leri Boşta olarak işaretle"
    
    def delete_subnet(self, request, queryset):
        subnet_list = queryset.values_list('subnet', flat=True).distinct()
        deleted_ips = IPAddress.objects.filter(subnet__in=subnet_list).delete()
        self.message_user(request, f"{deleted_ips[0]} IP addresses from subnets {', '.join(subnet_list)} successfully deleted.")
    delete_subnet.short_description = "Seçilen subnet’i ve ilgili IP adreslerini sil"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'IP Address List'
        return super(IPAddressAdmin, self).changelist_view(request, extra_context=extra_context)

    def ping_button(self, obj):
        return format_html(
            '<button class="ping-button" data-ip="{}">Ping</button>',
            obj.ip_address
        )
    ping_button.short_description = 'Ping'
    
    class Media: 
        js = ('admin/js/admin_ping.js',)
        
    
    def display_alan_10(self, obj):
    # Kullanıcının 'view_password' iznine sahip olup olmadığını kontrol eder
        if self.request.user.has_perm('ip_app.view_password'):
            return format_html(
                '''
                <input type="password" name="password_{0}" value="{1}" readonly>
                <button type="button" onclick="togglePasswordVisibility({0});">Göster</button>
                <script>
                    function togglePasswordVisibility(id) {{
                        var input = document.querySelector(`input[name='password_${{id}}']`);
                        var button = input.nextElementSibling;
                        if (input.type === 'password') {{
                            input.type = 'text';
                            button.textContent = 'Gizle';
                        }} else {{
                            input.type = 'password';
                            button.textContent = 'Göster';
                        }}
                    }}
                </script>
                ''',
                obj.id, obj.sifre
            )
        else:
            return '••••'

    display_alan_10.short_description = 'Şifre & Göster'
    
    def get_list_display(self, request):
        # Kullanıcının 'view_password' iznine sahip olup olmadığını kontrol eder
        if request.user.has_perm('ip_app.view_password'):
            return ('ip_address', 'status', 'ping_button', 'ip_link', 'public_ip_link', 'device_name','location', 'backbone', 'alt_router', 'ssid', 'device', 'seri_no', 'mac', 'username', 'display_alan_10','açıklama', 'edit_link')
        else:
            return ('ip_address', 'status', 'ping_button', 'ip_link', 'public_ip_link', 'device_name','location', 'backbone', 'alt_router', 'ssid', 'device', 'seri_no', 'mac', 'username','açıklama', 'edit_link')
    
    def changelist_view(self, request, extra_context=None):
        self.request = request
        return super().changelist_view(request, extra_context)

    
    def add_view(self, request, form_url='', extra_context=None):
        form = IPRangeForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            ip_input = form.cleaned_data['ip_address']
            subnet = form.cleaned_data.get('subnet')
            device_id = form.cleaned_data.get('device')
            device_name = form.cleaned_data.get('device_name')
            status = form.cleaned_data.get('status')
            backbone = form.cleaned_data.get('backbone')
            alt_router = form.cleaned_data.get('alt_router')
            ssid = form.cleaned_data.get('ssid')
            seri_no = form.cleaned_data.get('seri_no')
            mac = form.cleaned_data.get('mac')
            açıklama = form.cleaned_data.get('açıklama')
            try:
                # DeviceOption nesnesi bulunur
                device = DeviceOption.objects.filter(id=device_id).first() if device_id else None

                if '/' in ip_input:
                    # IP aralığı işlemi
                    network = ip_network(ip_input, strict=False)
                    existing_ips = set(IPAddress.objects.filter(ip_address__in=[str(ip) for ip in network.hosts()]).values_list('ip_address', flat=True))
                    ip_list = []
                    for ip in network.hosts():
                        ip_str = str(ip)
                        if ip_str not in existing_ips:
                            try:
                                IPAddress.objects.create(
                                    ip_address=ip_str,
                                    subnet=subnet,
                                    device=device,
                                    device_name=device_name,
                                    status=status,
                                    backbone=backbone,
                                    alt_router=alt_router,
                                    ssid=ssid,
                                    seri_no=seri_no,
                                    mac=mac,
                                    user=request.user,
                                    açıklama=açıklama,
                                )
                                ip_list.append(ip_str)
                            except IntegrityError as e:
                                self.message_user(request, f"The IP address {ip_str} could not be added due to a database error: {e}", level="error")
                    if ip_list:
                        self.message_user(request, f"{len(ip_list)} IP addresses from {ip_input} successfully added.")
                    else:
                        self.message_user(request, "All IP addresses in this range already exist or could not be added.", level="warning")
                else:
                    # Tekil IP adresi işlemi
                    if not IPAddress.objects.filter(ip_address=ip_input).exists():
                        try:
                            IPAddress.objects.create(
                                ip_address=ip_input,
                                subnet=subnet,
                                device=device,
                                device_name=device_name,
                                status=status,
                                backbone=backbone,
                                alt_router=alt_router,
                                ssid=ssid,
                                seri_no=seri_no,
                                mac=mac,
                                user=request.user,
                                açıklama = açıklama
                            )
                            self.message_user(request, f"Single IP address {ip_input} successfully added.")
                        except IntegrityError as e:
                            self.message_user(request, f"The IP address {ip_input} could not be added due to a database error: {e}", level="error")
                    else:
                        self.message_user(request, f"The IP address {ip_input} already exists.", level="warning")
                return self.changelist_view(request)
            except (AddressValueError, NetmaskValueError) as e:
                self.message_user(request, f"Invalid IP address or subnet: {e}", level="error")
            except Exception as e:
                self.message_user(request, f"An unexpected error occurred: {e}", level="error")
        else:
            if form.errors:
                self.message_user(request, "Form is not valid. Please correct the errors below.", level="error")

        extra_context = extra_context or {}
        extra_context['form'] = form
        return super().add_view(request, form_url, extra_context)


   
    
    def get_queryset(self, request):
        """IP adreslerini eklenme tarihine göre sıralı listele"""
        qs = super().get_queryset(request)
        return qs.order_by('-created_at', 'ip_address')
    
    def edit_link(self, obj):
        url = reverse('admin:ip_app_ipaddress_change', args=[obj.pk])
        return format_html('<a href="{}">Düzenle</a>', url)
    edit_link.short_description = 'Düzenle'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('ping-ip/', self.admin_site.admin_view(ping_ip), name='ping_ip'),
            path('edit/<int:pk>/', self.admin_site.admin_view(self.edit_view), name='ip-address-edit'),
        ]
        return custom_urls + urls

    def edit_view(self, request, pk):
        from django.shortcuts import get_object_or_404, render
        ip_address = get_object_or_404(IPAddress, pk=pk)
        form = IPAddressForm(request.POST or None, instance=ip_address, user=request.user)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                self.message_user(request, "IP Adresi başarıyla güncellendi.")
                return HttpResponseRedirect(reverse('admin:ip_app_ipaddress_changelist'))
        return render(request, 'admin/change_form.html', {'form': form, 'title': "Edit IP Address"})

    def ip_link(self, obj):
        ssh_url = f"ssh://{obj.username}:{obj.sifre}@{obj.ip_address}"
        return format_html('''
            <div class="dropdown">
                <button class="dropbtn">{}</button>
                <div class="dropdown-content">
                    <a href="http://{}" target="_blank">HTTP ile Aç</a>
                    <a href="winbox://{}">Winbox ile Aç</a>
                    <a href="{}">SSH ile Bağlan</a>
                </div>
            </div>
            <style>
                .dropbtn {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px;
                    border: none;
                    cursor: pointer;
                }}

                .dropdown {{
                    position: relative;
                    display: inline-block;
                }}

                .dropdown-content {{
                    display: none;
                    position: absolute;
                    background-color: #f9f9f9;
                    min-width: 160px;
                    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
                    z-index: 1;
                }}

                .dropdown-content a {{
                    color: black;
                    padding: 12px 16px;
                    text-decoration: none;
                    display: block;
                }}

                .dropdown-content a:hover {{background-color: #f1f1f1}}

                .dropdown:hover .dropdown-content {{
                    display: block;
                }}

                .dropdown:hover .dropbtn {{
                    background-color: #3e8e41;
                }}
            </style>
        ''', obj.ip_address, obj.ip_address, obj.ip_address, ssh_url)
    ip_link.short_description = 'IP Address'
    
    def public_ip_link(self, obj):
        if obj.public_ip:
            ssh_url = f"ssh://{obj.username}:{obj.sifre}@{obj.public_ip}"
            return format_html('''
                <div class="dropdown">
                    <button class="dropbtn">{}</button>
                    <div class="dropdown-content">
                        <a href="http://{}" target="_blank">HTTP ile Aç</a>
                        <a href="winbox://{}">Winbox ile Aç</a>
                        <a href="{}">SSH ile Bağlan</a>
                    </div>
                </div>
            ''', obj.public_ip, obj.public_ip, obj.public_ip, ssh_url)
        else:
            return "-"
    public_ip_link.short_description = 'Public IP'

    def select_all(self, request, queryset):
        selected = queryset.values_list('id', flat=True)
        self.message_user(request, f"Seçilen {len(selected)} IP adresi.")
    select_all.short_description = "Tüm Kayıtları Seç"
    
admin.site.register(IPAddress, IPAddressAdmin)