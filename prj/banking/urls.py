from django.urls import path

from . import views

urlpatterns = [
    path('admin/', views.vAdmin, name='admin'),
    path('admin/create/', views.vAdminCreate, name='admin_create'),
    path('admin/manage/', views.vAdminManage, name='admin_manage'),
    path('admin/manage/<slug:username>/balance/', views.vAdminManageBalance, name='admin_manage_balance'),
    path('admin/manage/<slug:username>/password/', views.vAdminManagePassword, name='admin_manage_pass'),
    path('admin/logs/', views.vAdminLogs, name='admin_logs'),

    path('', views.vIndex, name='index'),
    path('init/', views.vInit, name='init'),
    path('login/', views.vLogin, name='login'),
    path('create/', views.vCreate, name='create'),
    path('logout/', views.vLogout, name='logout'),
    path('user/<slug:username>/hello/', views.vHello, name="hello"),
    path('user/<slug:username>/send/', views.vSend, name="send"),
    path('user/<slug:username>/send/confirm', views.vSendConfirm, name="send_confirm"),
    path('user/<slug:username>/history/', views.vTransactions, name="history"),
]