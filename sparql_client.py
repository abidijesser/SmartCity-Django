"""
Client SPARQL pour Apache Fuseki
Permet d'effectuer des requêtes sur l'ontologie RDF
"""
import requests
from typing import List, Dict, Optional
import json

class SparqlClient:
    """Client pour interroger Apache Fuseki via SPARQL"""
    
    def __init__(self, fuseki_url: str = "http://localhost:3030/transport/query"):
        """
        Initialise le client SPARQL
        
        Args:
            fuseki_url: URL du endpoint SPARQL de Fuseki
        """
        self.fuseki_url = fuseki_url
        self.headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def query(self, sparql_query: str) -> List[Dict]:
        """
        Exécute une requête SPARQL SELECT et retourne les résultats
        
        Args:
            sparql_query: Requête SPARQL SELECT
            
        Returns:
            Liste de dictionnaires contenant les résultats
        """
        try:
            # Ajouter le PREFIX si nécessaire
            if "PREFIX" not in sparql_query:
                sparql_query = self._add_prefixes(sparql_query)
            
            params = {'query': sparql_query}
            response = requests.post(self.fuseki_url, data=params, headers=self.headers)
            response.raise_for_status()
            
            results = json.loads(response.text)
            return self._parse_results(results)
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la requête SPARQL: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Erreur lors du parsing JSON: {e}")
            return []
    
    def _add_prefixes(self, query: str) -> str:
        """Ajoute les prefixes OWL/RDF standards si absents"""
        prefixes = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
"""
        return prefixes + "\n" + query
    
    def _parse_results(self, results: dict) -> List[Dict]:
        """
        Parse les résultats SPARQL en liste de dictionnaires
        
        Args:
            results: Résultats JSON de SPARQL
            
        Returns:
            Liste de dictionnaires avec les résultats
        """
        parsed_results = []
        
        if 'results' in results and 'bindings' in results['results']:
            for binding in results['results']['bindings']:
                row = {}
                for key, value in binding.items():
                    row[key] = value.get('value', '')
                parsed_results.append(row)
        
        return parsed_results
    
    # ===== MÉTHODES SPÉCIFIQUES POUR L'ONTOLOGIE DE TRANSPORT =====
    
    def get_all_stations(self) -> List[Dict]:
        """Récupère toutes les stations"""
        query = """
SELECT ?station ?nom ?latitude ?longitude ?adresse ?type
WHERE {
    ?station rdf:type transport:Station .
    OPTIONAL { ?station transport:nom ?nom . }
    OPTIONAL { ?station transport:latitude ?latitude . }
    OPTIONAL { ?station transport:longitude ?longitude . }
    OPTIONAL { ?station transport:adresse ?adresse . }
    OPTIONAL { ?station rdf:type ?type . }
}
ORDER BY ?nom
"""
        return self.query(query)
    
    def get_stations_by_city(self, ville: str) -> List[Dict]:
        """Récupère les stations d'une ville"""
        query = """
SELECT ?station ?nom ?latitude ?longitude ?adresse
WHERE {
    ?station transport:situeDans ?ville .
    ?ville transport:nom "{}" .
    ?station rdf:type transport:Station .
    OPTIONAL { ?station transport:nom ?nom . }
    OPTIONAL { ?station transport:latitude ?latitude . }
    OPTIONAL { ?station transport:longitude ?longitude . }
    OPTIONAL { ?station transport:adresse ?adresse . }
}
""".format(ville)
        return self.query(query)
    
    def get_all_vehicles(self) -> List[Dict]:
        """Récupère tous les véhicules"""
        query = """
SELECT ?vehicule ?nom ?matricule ?capacite ?vitesseMoyenne ?type
WHERE {
    ?vehicule rdf:type transport:Véhicule .
    OPTIONAL { ?vehicule transport:nom ?nom . }
    OPTIONAL { ?vehicule transport:matricule ?matricule . }
    OPTIONAL { ?vehicule transport:capacite ?capacite . }
    OPTIONAL { ?vehicule transport:vitesseMoyenne ?vitesseMoyenne . }
    OPTIONAL { ?vehicule rdf:type ?type . }
}
ORDER BY ?nom
"""
        return self.query(query)
    
    def get_trips_by_user(self, user_uri: str) -> List[Dict]:
        """Récupère les trajets d'un utilisateur"""
        query = """
SELECT ?trajet ?heureDepart ?heureArrivee ?duree ?distance ?depart ?arrivee
WHERE {
    ?utilisateur rdf:type transport:Utilisateur .
    ?utilisateur transport:effectueTrajet ?trajet .
    OPTIONAL { ?trajet transport:heureDepart ?heureDepart . }
    OPTIONAL { ?trajet transport:heureArrivee ?heureArrivee . }
    OPTIONAL { ?trajet transport:dureeTrajet ?duree . }
    OPTIONAL { ?trajet transport:distanceTrajet ?distance . }
    OPTIONAL { 
        ?trajet transport:aPourDepart ?stationDep .
        ?stationDep transport:nom ?depart .
    }
    OPTIONAL { 
        ?trajet transport:aPourArrivee ?stationArr .
        ?stationArr transport:nom ?arrivee .
    }
}
""".replace('FILTER(?utilisateur = <' + user_uri + '>)', '')
        return self.query(query)
    
    def get_horaires_by_station(self, station_nom: str) -> List[Dict]:
        """Récupère les horaires d'une station"""
        query = """
SELECT ?horaire ?heureDepart ?heureArrivee ?trajet
WHERE {
    ?station transport:nom "{}" .
    ?trajet transport:aPourDepart ?station .
    ?trajet transport:aPourHoraire ?horaire .
    ?horaire transport:heureDepart ?heureDepart .
    ?horaire transport:heureArrivee ?heureArrivee .
}
ORDER BY ?heureDepart
""".format(station_nom)
        return self.query(query)
    
    def get_parkings_near_station(self, station_nom: str) -> List[Dict]:
        """Récupère les parkings près d'une station"""
        query = """
SELECT ?parking ?nom ?placesDisponibles ?nombrePlaces ?adresse ?latitude ?longitude
WHERE {
    ?station transport:nom "{}" .
    ?station transport:procheDe ?parking .
    ?parking rdf:type transport:Parking .
    OPTIONAL { ?parking transport:nom ?nom . }
    OPTIONAL { ?parking transport:placesDisponibles ?placesDisponibles . }
    OPTIONAL { ?parking transport:nombrePlaces ?nombrePlaces . }
    OPTIONAL { ?parking transport:adresse ?adresse . }
    OPTIONAL { ?parking transport:latitude ?latitude . }
    OPTIONAL { ?parking transport:longitude ?longitude . }
}
""".format(station_nom)
        return self.query(query)
    
    def get_traffic_events(self) -> List[Dict]:
        """Récupère tous les événements de trafic"""
        query = """
SELECT ?evenement ?typeEvenement ?dateEvenement ?latitude ?longitude
WHERE {
    ?evenement rdf:type transport:ÉvénementTrafic .
    OPTIONAL { ?evenement transport:typeEvenement ?typeEvenement . }
    OPTIONAL { ?evenement transport:dateEvenement ?dateEvenement . }
    OPTIONAL { ?evenement transport:latitude ?latitude . }
    OPTIONAL { ?evenement transport:longitude ?longitude . }
}
ORDER BY DESC(?dateEvenement)
LIMIT 20
"""
        return self.query(query)
    
    def search_trips(self, depart: str, arrivee: str) -> List[Dict]:
        """Recherche des trajets entre deux stations"""
        query = """
SELECT DISTINCT ?trajet ?heureDepart ?heureArrivee ?duree ?distance ?vehicule
WHERE {
    ?trajet rdf:type transport:Trajet .
    
    ?trajet transport:aPourDepart ?stationDep .
    ?stationDep transport:nom ?depart .
    
    ?trajet transport:aPourArrivee ?stationArr .
    ?stationArr transport:nom ?arrivee .
    
    OPTIONAL { ?trajet transport:heureDepart ?heureDepart . }
    OPTIONAL { ?trajet transport:heureArrivee ?heureArrivee . }
    OPTIONAL { ?trajet transport:dureeTrajet ?duree . }
    OPTIONAL { ?trajet transport:distanceTrajet ?distance . }
    OPTIONAL { 
        ?trajet transport:utiliseVehicule ?vehicule .
        ?vehicule transport:nom ?vehiculeNom .
    }
}
"""
        # Pour l'instant, on recherche exactement les noms
        # On pourrait améliorer avec LIKE ou CONTAINS
        return self.query(query)


# Instance globale du client
sparql_client = SparqlClient()

