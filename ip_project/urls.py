"""
URL configuration for ip_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from ip_app.views import ip_calculator_view, ip_list_view, search_results, ping_ip, update_ip_status, check_ip_status

urlpatterns = [
    path('admin/', admin.site.urls),
    # IP adresleri listesi ve arama
    path('', ip_list_view, name='ip_list_view'),
    path('search/', search_results, name='search_results'),

    # Ping işlemleri
    path('ping-ip/', ping_ip, name='ping_ip'),
    
    # IP adresi güncelleme
    path('update-ip-status/', update_ip_status, name='update_ip_status'),
    path('check-ip-status/', check_ip_status, name='check_ip_status'),
    
    path('ip-calculator/', ip_calculator_view, name='ip_calculator'),
    
]




