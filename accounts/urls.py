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
    path('trajets/<path:trajet_uri>/edit/', views.trajet_detail_view, name='trajet_edit'),
    path('trajets/<path:trajet_uri>/delete/', views.trajet_delete_view, name='trajet_delete'),
    
    # Gestion CRUD des stations (Gestionnaires uniquement)
    path('stations/', views.stations_list_view, name='stations_list'),
    path('stations/create/', views.station_create_view, name='station_create'),
    path('stations/<path:station_uri>/edit/', views.station_detail_view, name='station_edit'),
    path('stations/<path:station_uri>/delete/', views.station_delete_view, name='station_delete'),
    # Gestion CRUD des horaires
    path('horaires/', views.horaires_list_view, name='horaires_list'),
    path('horaires/create/', views.horaire_create_view, name='horaire_create'),
    path('horaires/<path:horaire_uri>/edit/', views.horaire_detail_view, name='horaire_edit'),
    path('horaires/<path:horaire_uri>/delete/', views.horaire_delete_view, name='horaire_delete'),
    
    # Gestion CRUD des parkings
    path('parkings/', views.parkings_list_view, name='parkings_list'),
    path('parkings/create/', views.parking_create_view, name='parking_create'),
    path('parkings/<path:parking_uri>/edit/', views.parking_detail_view, name='parking_edit'),
    path('parkings/<path:parking_uri>/delete/', views.parking_delete_view, name='parking_delete'),
    
    # Gestion CRUD des événements
    path('evenements/', views.evenements_list_view, name='evenements_list'),
    path('evenements/create/', views.evenement_create_view, name='evenement_create'),
    path('evenements/<path:evenement_uri>/edit/', views.evenement_detail_view, name='evenement_edit'),
    path('evenements/<path:evenement_uri>/delete/', views.evenement_delete_view, name='evenement_delete'),
    
    # Gestion CRUD des capteurs
    path('capteurs/', views.capteurs_list_view, name='capteurs_list'),
    path('capteurs/create/', views.capteur_create_view, name='capteur_create'),
    path('capteurs/<path:capteur_uri>/edit/', views.capteur_detail_view, name='capteur_edit'),
    path('capteurs/<path:capteur_uri>/delete/', views.capteur_delete_view, name='capteur_delete'),
    
    # Gestion CRUD des routes
    path('routes/', views.routes_list_view, name='routes_list'),
    path('routes/create/', views.route_create_view, name='route_create'),
    path('routes/<path:route_uri>/edit/', views.route_detail_view, name='route_edit'),
    path('routes/<path:route_uri>/delete/', views.route_delete_view, name='route_delete'),
    
    # Gestion CRUD des villes
    path('villes/', views.villes_list_view, name='villes_list'),
    path('villes/create/', views.ville_create_view, name='ville_create'),
    path('villes/<path:ville_uri>/edit/', views.ville_detail_view, name='ville_edit'),
    path('villes/<path:ville_uri>/delete/', views.ville_delete_view, name='ville_delete'),

    # Endpoints AI (JSON)
    path('ai/stations/suggest/', views.ai_station_suggest_view, name='ai_station_suggest'),
    path('ai/trajets/recommend/', views.ai_trajet_recommend_view, name='ai_trajet_recommend'),
    # Compatibilité si l'utilisateur saisit un préfixe 'accounts/' dans l'URL
    path('accounts/ai/stations/suggest/', views.ai_station_suggest_view),
    path('accounts/ai/trajets/recommend/', views.ai_trajet_recommend_view),
]

