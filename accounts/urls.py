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
    
    # Gestion CRUD des véhicules
    path('vehicules/', views.vehicules_list_view, name='vehicules_list'),
    path('vehicules/create/', views.vehicule_create_view, name='vehicule_create'),
    path('vehicules/<path:vehicule_uri>/edit/', views.vehicule_detail_view, name='vehicule_edit'),
    path('vehicules/<path:vehicule_uri>/delete/', views.vehicule_delete_view, name='vehicule_delete'),
    
    # Gestion CRUD des trajets (Conducteurs uniquement)
    path('trajets/', views.trajets_list_view, name='trajets_list'),
    path('trajets/create/', views.trajet_create_view, name='trajet_create'),
    path('trajets/<path:trajet_uri>/delete/', views.trajet_delete_view, name='trajet_delete'),
    
    # Gestion CRUD des stations (Gestionnaires uniquement)
    path('stations/', views.stations_list_view, name='stations_list'),
    path('stations/create/', views.station_create_view, name='station_create'),
    path('stations/<path:station_uri>/delete/', views.station_delete_view, name='station_delete'),
]

