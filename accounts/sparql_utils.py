"""
Utilitaires SPARQL pour l'application Django
"""
from typing import List, Dict, Optional
import requests
import json
import logging

logger = logging.getLogger(__name__)

class TransportSparqlClient:
    """Client SPARQL pour l'ontologie de transport"""
    
    # PREFIXES de l'ontologie
    TRANSPORT_PREFIX = "http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/"
    
    def __init__(self, fuseki_url: str = "http://localhost:3030/transport/query"):
        self.fuseki_url = fuseki_url
        self.headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def execute_query(self, sparql_query: str) -> List[Dict]:
        """Exécute une requête SPARQL SELECT"""
        try:
            # Ajouter les prefixes si nécessaire
            if "PREFIX" not in sparql_query:
                sparql_query = self._add_prefixes() + "\n" + sparql_query
            
            params = {'query': sparql_query}
            response = requests.post(self.fuseki_url, data=params, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            results = json.loads(response.text)
            return self._parse_results(results)
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"Fuseki indisponible: {e}")
            return []
        except requests.exceptions.Timeout as e:
            logger.warning(f"Timeout SPARQL: {e}")
            return []
        except Exception as e:
            logger.error(f"Erreur requête SPARQL: {e}")
            return []
    
    def _add_prefixes(self) -> str:
        """Ajoute les prefixes standards"""
        return """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX transport: <http://www.semanticweb.org/dell/ontologies/2025/9/untitled-ontology-6/>
"""
    
    def _parse_results(self, results: dict) -> List[Dict]:
        """Parse les résultats SPARQL"""
        parsed = []
        if 'results' in results and 'bindings' in results['results']:
            for binding in results['results']['bindings']:
                row = {}
                for key, value in binding.items():
                    row[key] = value.get('value', '')
                parsed.append(row)
        return parsed
    
    # ===== REQUÊTES SPÉCIFIQUES =====
    
    def get_all_stations(self) -> List[Dict]:
        """Récupère toutes les stations avec leurs types"""
        query = """
SELECT ?station ?nom ?latitude ?longitude ?adresse ?type
WHERE {
    ?station rdf:type/rdfs:subClassOf* transport:Station .
    OPTIONAL { ?station transport:nom ?nom }
    OPTIONAL { ?station transport:latitude ?latitude }
    OPTIONAL { ?station transport:longitude ?longitude }
    OPTIONAL { ?station transport:adresse ?adresse }
    OPTIONAL { 
        ?station rdf:type ?type .
        FILTER (?type != transport:Station)
    }
}
ORDER BY ?nom
"""
        return self.execute_query(query)
    
    def get_vehicles(self) -> List[Dict]:
        """Récupère tous les véhicules"""
        query = """
SELECT ?vehicule ?nom ?matricule ?capacite ?vitesseMoyenne ?type
WHERE {
    ?vehicule rdf:type/rdfs:subClassOf* transport:Véhicule .
    OPTIONAL { ?vehicule transport:nom ?nom }
    OPTIONAL { ?vehicule transport:matricule ?matricule }
    OPTIONAL { ?vehicule transport:capacite ?capacite }
    OPTIONAL { ?vehicule transport:vitesseMoyenne ?vitesseMoyenne }
    OPTIONAL { 
        ?vehicule rdf:type ?type .
        FILTER (?type != transport:Véhicule)
    }
}
ORDER BY ?nom
"""
        return self.execute_query(query)
    
    def search_trips(self, depart: Optional[str] = None, arrivee: Optional[str] = None) -> List[Dict]:
        """Recherche des trajets avec filtres optionnels"""
        query = """
SELECT DISTINCT ?trajet ?heureDepart ?heureArrivee ?duree ?distance ?type ?depart ?arrivee
WHERE {
    ?trajet rdf:type transport:Trajet .
    OPTIONAL { ?trajet transport:heureDepart ?heureDepart }
    OPTIONAL { ?trajet transport:heureArrivee ?heureArrivee }
    OPTIONAL { ?trajet transport:dureeTrajet ?duree }
    OPTIONAL { ?trajet transport:distanceTrajet ?distance }
    OPTIONAL { 
        ?trajet rdf:type ?type .
        FILTER (?type != transport:Trajet)
    }
    OPTIONAL {
        ?trajet transport:aPourDepart ?stationDep .
        ?stationDep transport:nom ?depart
    }
    OPTIONAL {
        ?trajet transport:aPourArrivee ?stationArr .
        ?stationArr transport:nom ?arrivee
    }
"""
        if depart:
            query += f'\n    FILTER (CONTAINS(LCASE(STR(?depart)), LCASE("{depart}")))'
        if arrivee:
            query += f'\n    FILTER (CONTAINS(LCASE(STR(?arrivee)), LCASE("{arrivee}")))'
        
        query += "\n}"
        return self.execute_query(query)
    
    def get_traffic_events(self, limit: int = 10) -> List[Dict]:
        """Récupère les événements de trafic récents"""
        query = f"""
SELECT ?evenement ?typeEvenement ?dateEvenement ?latitude ?longitude
WHERE {{
    ?evenement rdf:type/rdfs:subClassOf* transport:ÉvénementTrafic .
    OPTIONAL {{ ?evenement transport:typeEvenement ?typeEvenement }}
    OPTIONAL {{ ?evenement transport:dateEvenement ?dateEvenement }}
    OPTIONAL {{ ?evenement transport:latitude ?latitude }}
    OPTIONAL {{ ?evenement transport:longitude ?longitude }}
}}
ORDER BY DESC(?dateEvenement)
LIMIT {limit}
"""
        return self.execute_query(query)
    
    def get_parkings_by_station_name(self, station_nom: str) -> List[Dict]:
        """Récupère les parkings proches d'une station"""
        query = f"""
SELECT ?parking ?nom ?placesDisponibles ?nombrePlaces ?adresse ?latitude ?longitude
WHERE {{
    ?station transport:nom "{station_nom}" .
    ?station transport:procheDe ?parking .
    ?parking rdf:type/rdfs:subClassOf* transport:Parking .
    OPTIONAL {{ ?parking transport:nom ?nom }}
    OPTIONAL {{ ?parking transport:placesDisponibles ?placesDisponibles }}
    OPTIONAL {{ ?parking transport:nombrePlaces ?nombrePlaces }}
    OPTIONAL {{ ?parking transport:adresse ?adresse }}
    OPTIONAL {{ ?parking transport:latitude ?latitude }}
    OPTIONAL {{ ?parking transport:longitude ?longitude }}
}}
"""
        return self.execute_query(query)


# Instance globale du client
sparql = TransportSparqlClient()

# Fonction pour vérifier la disponibilité de Fuseki
def check_fuseki_availability():
    """Vérifie si Fuseki est disponible"""
    try:
        response = requests.get("http://localhost:3030", timeout=2)
        return response.status_code == 200
    except:
        return False

FUSEKI_AVAILABLE = check_fuseki_availability()

