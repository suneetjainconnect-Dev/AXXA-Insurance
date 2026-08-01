from django.urls import path
from . import views

app_name = 'insurance'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('policies/', views.policy_list, name='policy_list'),
    path('policies/<int:pk>/', views.policy_detail, name='policy_detail'),
    path('policies/catalog/', views.policy_catalog, name='policy_catalog'),
    path('claims/', views.claim_list, name='claim_list'),
    path('claims/<int:pk>/', views.claim_detail, name='claim_detail'),
    path('policies/<int:policy_id>/claim/', views.create_claim, name='create_claim'),
    path('claims/<int:claim_id>/upload-document/', views.upload_document, name='upload_document'),
    path('profile/', views.profile, name='profile'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('calculator/', views.premium_calculator, name='premium_calculator'),
]
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views_auth import register, login_view, logout_view

app_name = 'insurance'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('policies/', views.policy_list, name='policy_list'),
    path('policies/<int:pk>/', views.policy_detail, name='policy_detail'),
    path('policies/catalog/', views.policy_catalog, name='policy_catalog'),
    path('claims/', views.claim_list, name='claim_list'),
    path('claims/<int:pk>/', views.claim_detail, name='claim_detail'),
    path('policies/<int:policy_id>/claim/', views.create_claim, name='create_claim'),
    path('claims/<int:claim_id>/upload-document/', views.upload_document, name='upload_document'),
    path('profile/', views.profile, name='profile'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('calculator/', views.premium_calculator, name='premium_calculator'),
    
    # Authentication URLs
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]