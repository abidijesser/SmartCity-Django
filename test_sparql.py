"""
Script pour tester la connexion SPARQL avec Fuseki
"""
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classProject.settings')
django.setup()

from accounts.sparql_utils import sparql, check_fuseki_availability

def test_fuseki_connection():
    """Teste la connexion a Fuseki"""
    print("=" * 60)
    print("TEST DE CONNEXION APACHE FUSEKI")
    print("=" * 60)
    
    # Verifier la disponibilite
    is_available = check_fuseki_availability()
    print(f"\nFuseki disponible: {is_available}")
    
    if not is_available:
        print("\nERREUR: Fuseki n'est pas accessible!")
        print("\nActions a faire:")
        print("1. Demarrer Apache Fuseki:")
        print("   cd C:\\fuseki\\apache-jena-fuseki-5.6.0")
        print("   .\\fuseki-server")
        print("\n2. Verifier sur: http://localhost:3030")
        return False
    
    print(f"\nURL du endpoint: http://localhost:3030/transport/query")
    
    # Tester une requete simple
    print("\nTest de requete: Lister toutes les stations...")
    try:
        stations = sparql.get_all_stations()
        print(f"NOMBRE de stations trouvees: {len(stations)}")
        
        if stations:
            print("\nExemple de stations:")
            for i, station in enumerate(stations[:3], 1):
                print(f"   {i}. {station.get('nom', 'N/A')}")
        
    except Exception as e:
        print(f"ERREUR: {e}")
        return False
    
    # Tester les vehicules
    print("\nTest: Lister tous les vehicules...")
    try:
        vehicles = sparql.get_vehicles()
        print(f"NOMBRE de vehicules trouves: {len(vehicles)}")
        
        if vehicles:
            print("\nExemple de vehicules:")
            for i, vehicle in enumerate(vehicles[:3], 1):
                print(f"   {i}. {vehicle.get('nom', 'N/A')}")
        
    except Exception as e:
        print(f"ERREUR: {e}")
    
    # Test evenements
    print("\nTest: Lister les evenements de trafic...")
    try:
        events = sparql.get_traffic_events(limit=3)
        print(f"NOMBRE d'evenements trouves: {len(events)}")
        
        if events:
            print("\nExemple d'evenements:")
            for i, event in enumerate(events, 1):
                print(f"   {i}. {event.get('typeEvenement', 'N/A')}")
        
    except Exception as e:
        print(f"ERREUR: {e}")
    
    print("\n" + "=" * 60)
    print("TESTS TERMINES")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    test_fuseki_connection()
