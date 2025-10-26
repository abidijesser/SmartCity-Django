from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    
    # Pages de test RDF/Fuseki
    path('test/', views.test_home_view, name='test_home'),
    path('test/villes/', views.test_villes_view, name='test_villes'),
    path('test/vehicules/', views.test_vehicules_view, name='test_vehicules'),
    path('test/stations/', views.test_stations_view, name='test_stations'),
]

