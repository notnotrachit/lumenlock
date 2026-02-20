"""
URL configuration for lumenlock project.

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
from django.urls import path, include
from wallet.views import home, create_wallet, check_balance, send_money, dashboard, transaction_history

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', home),
    path('create_wallet', create_wallet, name='create_wallet'),
    path('check_balance', check_balance),
    path('send_money', send_money, name='send_tokens'),
    path('dashboard', dashboard, name='dashboard'),
    path('transaction_history', transaction_history, name='transaction_history'),
]