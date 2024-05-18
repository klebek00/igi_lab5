"""
URL configuration for PharmacyApp project.

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
from django.urls import path, re_path, include
from pharmacy import views, statistics
from django.conf.urls.static import static
from django.conf import settings

user_patterns = [
    re_path(r'orders', views.UserOrdersListView.as_view(), name='orders_list'),
    re_path(r'order/(?P<jk>\d+)', views.UserOrderView.as_view(), name='user_order'),
]

urlpatterns = [
    #path(' ', admin.site.urls),
    #path('', views.home, name='home')
    path('', views.home, name='home'),

    path('admin/', admin.site.urls),
    path('register/', views.UserRegistrationView.as_view(), name="register"),
    path('login/', views.UserLoginView.as_view(), name="login"),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('about/', views.about_company, name='about'),
    path('news/', views.news, name='news'),
    path('faqs/', views.faqs, name='terms'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy-policy', views.privacy_policy, name='privacy_policy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('review/create/', views.ReviewCreateView.as_view(), name='add_review'),
    path('review/<int:review_id>/edit/', views.ReviewEditView.as_view(), name='edit_review'),
    path('review/<int:review_id>/delete/', views.ReviewDeleteView.as_view(), name='delete_review'),
    path('promocodes/', views.promocodes, name="promocodes"),
    
    path('medicines/', views.MedicinesListView.as_view(), name='medicines'),
    path('medicines/<int:pk>/', views.MedicinesDetailView.as_view(), name='medicine_detail'), 
    path('medicines/new/', views.MedicineCreateView.as_view(), name='medicine_create'),
    path('medicines/<int:pk>/edit/',views.MedicineUpdateView.as_view(), name='medicine_edit'),   
    path('medicines/<int:pk>/delete/', views.MedicineDeleteView.as_view(), name='delete_med'),

    path('catigories/', views.CatigoriesListView.as_view(), name='catigories'),

    path('departments/', views.DepartmentInfo.as_view(), name='departments'),
    path('departments/new/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/edit/',views.DepartmentUpdateView.as_view(), name='department_edit'),   
    path('departments/<int:pk>/delete/', views.DepartmentDeleteView.as_view(), name='delete_dep'),

    re_path(r'medicines/(?P<pk>\d+)/order/create/$', views.OrderCreateView.as_view(), name='create_order'),
    re_path(r'user/(?P<pk>\d+)/', include(user_patterns)),

    path('suppliers/', views.SupplierListView.as_view(), name='suppliers'),
    path('suppliers/new/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_edit'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),

    path('orders/', views.OrderListView.as_view(), name='orders'),

    path('clients', statistics.clients, name='clients'),
    path('medic_stat', statistics.medicine, name='tours_stat'),

    path('sales', statistics.sales, name='sales'),
    path('revenue_chart', statistics.department_revenue_chart, name='department_revenue_chart'),
    path('diagramm', statistics.class_diagramm, name='model_diagramm'),
    
    path('api/medical_facts/', views.MedicalFactsView.as_view(), name='medical_facts'),
    path('api/rx/', views.RxView.as_view(), name='rx_search'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
