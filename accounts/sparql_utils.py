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
        self.update_url = fuseki_url.replace('/query', '/update')
        self.headers = {
            'Accept': 'application/sparql-results+json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.update_headers = {
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
    
    # ===== MÉTHODES DE MISE À JOUR (INSERT/DELETE) =====
    
    def execute_update(self, update_query: str) -> bool:
        """Exécute une requête SPARQL UPDATE (INSERT/DELETE)"""
        try:
            # Ajouter les prefixes si nécessaire
            if "PREFIX" not in update_query:
                update_query = self._add_prefixes() + "\n" + update_query
            
            params = {'update': update_query}
            response = requests.post(self.update_url, data=params, headers=self.update_headers, timeout=5)
            response.raise_for_status()
            return True
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Fuseki indisponible pour UPDATE: {e}")
            return False
        except Exception as e:
            logger.error(f"Erreur requête SPARQL UPDATE: {e}")
            return False
    
    def create_vehicule(self, nom: str, type_vehicule: str, matricule: str = "", capacite: int = None, vitesse_moyenne: float = None) -> bool:
        """Crée un nouveau véhicule dans l'ontologie"""
        # Générer un URI unique
        uri_safe_nom = nom.replace(" ", "_").replace("'", "")
        vehicule_uri = f"{self.TRANSPORT_PREFIX}Vehicule_{uri_safe_nom}"
        
        # Construire la requête INSERT
        insert_query = f"""
INSERT DATA {{
    <{vehicule_uri}> rdf:type transport:Véhicule ;
                     rdf:type transport:{type_vehicule} ;
                     transport:nom "{nom}" .
"""
        
        if matricule:
            insert_query += f'    <{vehicule_uri}> transport:matricule "{matricule}" .\n'
        
        if capacite is not None:
            insert_query += f'    <{vehicule_uri}> transport:capacite "{capacite}"^^xsd:integer .\n'
        
        if vitesse_moyenne is not None:
            insert_query += f'    <{vehicule_uri}> transport:vitesseMoyenne "{vitesse_moyenne}"^^xsd:float .\n'
        
        insert_query += "}"
        
        return self.execute_update(insert_query)
    
    def delete_vehicule(self, vehicule_uri: str) -> bool:
        """Supprime un véhicule de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{vehicule_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_vehicule(self, vehicule_uri: str, nom: str = None, matricule: str = None, capacite: int = None, vitesse_moyenne: float = None) -> bool:
        """Met à jour un véhicule existant"""
        if not any([nom is not None, matricule is not None, capacite is not None, vitesse_moyenne is not None]):
            return True
        
        # Construire la requête DELETE/INSERT
        update_query = f"""
DELETE {{
    <{vehicule_uri}> transport:nom ?oldNom ;
                     transport:matricule ?oldMatricule ;
                     transport:capacite ?oldCapacite ;
                     transport:vitesseMoyenne ?oldVitesse .
}}
INSERT {{
"""
        
        if nom is not None:
            update_query += f'    <{vehicule_uri}> transport:nom "{nom}" .\n'
        if matricule is not None:
            update_query += f'    <{vehicule_uri}> transport:matricule "{matricule}" .\n'
        if capacite is not None:
            update_query += f'    <{vehicule_uri}> transport:capacite "{capacite}"^^xsd:integer .\n'
        if vitesse_moyenne is not None:
            update_query += f'    <{vehicule_uri}> transport:vitesseMoyenne "{vitesse_moyenne}"^^xsd:float .\n'
        
        update_query += f"""
}}
WHERE {{
    <{vehicule_uri}> rdf:type ?type .
    OPTIONAL {{ <{vehicule_uri}> transport:nom ?oldNom }}
    OPTIONAL {{ <{vehicule_uri}> transport:matricule ?oldMatricule }}
    OPTIONAL {{ <{vehicule_uri}> transport:capacite ?oldCapacite }}
    OPTIONAL {{ <{vehicule_uri}> transport:vitesseMoyenne ?oldVitesse }}
}}
"""
        
        return self.execute_update(update_query)
    
    def addTrajet(self, depart_station_uri: str, arrivee_station_uri: str, 
                  vehicule_uri: str = None, heure_depart: str = None, 
                  heure_arrivee: str = None, distance: float = None, 
                  duree: float = None, nom_trajet: str = None) -> bool:
        """
        Crée un nouveau trajet dans l'ontologie
        
        Args:
            depart_station_uri: URI de la station de départ (requis)
            arrivee_station_uri: URI de la station d'arrivée (requis)
            vehicule_uri: URI du véhicule utilisé (optionnel)
            heure_depart: Heure de départ au format ISO 8601 (optionnel)
            heure_arrivee: Heure d'arrivée au format ISO 8601 (optionnel)
            distance: Distance du trajet en km (optionnel)
            duree: Durée du trajet en heures (optionnel)
            nom_trajet: Nom du trajet pour générer l'URI (optionnel)
            
        Returns:
            bool: True si succès, False sinon
        """
        # Générer un URI unique pour le trajet
        if nom_trajet:
            uri_safe_nom = nom_trajet.replace(" ", "_").replace("'", "").replace("-", "_")
        else:
            # Générer un nom basé sur les stations
            import time
            uri_safe_nom = f"Trajet_{int(time.time())}"
        
        trajet_uri = f"{self.TRANSPORT_PREFIX}{uri_safe_nom}"
        
        # Construire la requête INSERT
        insert_query = f"""
INSERT DATA {{
    <{trajet_uri}> rdf:type transport:Trajet ;
                   transport:aPourDepart <{depart_station_uri}> ;
                   transport:aPourArrivee <{arrivee_station_uri}> .
"""
        
        # Ajouter les propriétés optionnelles
        if vehicule_uri:
            insert_query += f'    <{trajet_uri}> transport:utiliseVehicule <{vehicule_uri}> .\n'
        
        if heure_depart:
            insert_query += f'    <{trajet_uri}> transport:heureDepart "{heure_depart}"^^xsd:dateTime .\n'
        
        if heure_arrivee:
            insert_query += f'    <{trajet_uri}> transport:heureArrivee "{heure_arrivee}"^^xsd:dateTime .\n'
        
        if distance is not None:
            insert_query += f'    <{trajet_uri}> transport:distanceTrajet "{distance}"^^xsd:float .\n'
        
        if duree is not None:
            insert_query += f'    <{trajet_uri}> transport:dureeTrajet "{duree}"^^xsd:float .\n'
        
        insert_query += "}"
        
        return self.execute_update(insert_query)
    
    def get_all_trajets(self) -> List[Dict]:
        """Récupère tous les trajets avec leurs détails"""
        query = """
SELECT ?trajet ?heureDepart ?heureArrivee ?dureeTrajet ?distanceTrajet 
       ?departStation ?departNom ?arriveeStation ?arriveeNom 
       ?vehicule ?vehiculeNom
WHERE {
    ?trajet rdf:type transport:Trajet .
    
    # Station de départ
    OPTIONAL { 
        ?trajet transport:aPourDepart ?departStation .
        ?departStation transport:nom ?departNom
    }
    
    # Station d'arrivée
    OPTIONAL { 
        ?trajet transport:aPourArrivee ?arriveeStation .
        ?arriveeStation transport:nom ?arriveeNom
    }
    
    # Véhicule
    OPTIONAL {
        ?trajet transport:utiliseVehicule ?vehicule .
        ?vehicule transport:nom ?vehiculeNom
    }
    
    # Propriétés du trajet
    OPTIONAL { ?trajet transport:heureDepart ?heureDepart }
    OPTIONAL { ?trajet transport:heureArrivee ?heureArrivee }
    OPTIONAL { ?trajet transport:dureeTrajet ?dureeTrajet }
    OPTIONAL { ?trajet transport:distanceTrajet ?distanceTrajet }
}
ORDER BY ?heureDepart
"""
        return self.execute_query(query)
    
    def delete_trajet(self, trajet_uri: str) -> bool:
        """Supprime un trajet de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{trajet_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_trajet(self, trajet_uri: str, depart_station_uri: str = None, 
                     arrivee_station_uri: str = None, vehicule_uri: str = None,
                     heure_depart: str = None, heure_arrivee: str = None,
                     distance: float = None, duree: float = None) -> bool:
        """
        Met à jour un trajet existant
        
        Args:
            trajet_uri: URI du trajet à mettre à jour
            depart_station_uri: Nouvelle URI de la station de départ (optionnel)
            arrivee_station_uri: Nouvelle URI de la station d'arrivée (optionnel)
            vehicule_uri: Nouvelle URI du véhicule (optionnel)
            heure_depart: Nouvelle heure de départ (optionnel)
            heure_arrivee: Nouvelle heure d'arrivée (optionnel)
            distance: Nouvelle distance (optionnel)
            duree: Nouvelle durée (optionnel)
            
        Returns:
            bool: True si succès, False sinon
        """
        if not any([depart_station_uri, arrivee_station_uri, vehicule_uri, 
                   heure_depart, heure_arrivee, distance is not None, duree is not None]):
            return True
        
        # Construire la requête DELETE/INSERT
        update_query = f"""
DELETE {{
    <{trajet_uri}> transport:aPourDepart ?oldDepart ;
                   transport:aPourArrivee ?oldArrivee ;
                   transport:utiliseVehicule ?oldVehicule ;
                   transport:heureDepart ?oldHeureDepart ;
                   transport:heureArrivee ?oldHeureArrivee ;
                   transport:distanceTrajet ?oldDistance ;
                   transport:dureeTrajet ?oldDuree .
}}
INSERT {{
"""
        
        if depart_station_uri:
            update_query += f'    <{trajet_uri}> transport:aPourDepart <{depart_station_uri}> .\n'
        if arrivee_station_uri:
            update_query += f'    <{trajet_uri}> transport:aPourArrivee <{arrivee_station_uri}> .\n'
        if vehicule_uri:
            update_query += f'    <{trajet_uri}> transport:utiliseVehicule <{vehicule_uri}> .\n'
        if heure_depart:
            update_query += f'    <{trajet_uri}> transport:heureDepart "{heure_depart}"^^xsd:dateTime .\n'
        if heure_arrivee:
            update_query += f'    <{trajet_uri}> transport:heureArrivee "{heure_arrivee}"^^xsd:dateTime .\n'
        if distance is not None:
            update_query += f'    <{trajet_uri}> transport:distanceTrajet "{distance}"^^xsd:float .\n'
        if duree is not None:
            update_query += f'    <{trajet_uri}> transport:dureeTrajet "{duree}"^^xsd:float .\n'
        
        update_query += f"""
}}
WHERE {{
    <{trajet_uri}> rdf:type transport:Trajet .
    OPTIONAL {{ <{trajet_uri}> transport:aPourDepart ?oldDepart }}
    OPTIONAL {{ <{trajet_uri}> transport:aPourArrivee ?oldArrivee }}
    OPTIONAL {{ <{trajet_uri}> transport:utiliseVehicule ?oldVehicule }}
    OPTIONAL {{ <{trajet_uri}> transport:heureDepart ?oldHeureDepart }}
    OPTIONAL {{ <{trajet_uri}> transport:heureArrivee ?oldHeureArrivee }}
    OPTIONAL {{ <{trajet_uri}> transport:distanceTrajet ?oldDistance }}
    OPTIONAL {{ <{trajet_uri}> transport:dureeTrajet ?oldDuree }}
}}
"""
        
        return self.execute_update(update_query)
    
    # ===== MÉTHODES POUR GÉRER LES STATIONS =====
    
    def addStation(self, nom: str, type_station: str, adresse: str = None,
                   latitude: float = None, longitude: float = None,
                   ville_uri: str = None) -> bool:
        """
        Crée une nouvelle station dans l'ontologie
        
        Args:
            nom: Nom de la station (requis)
            type_station: Type (StationBus, StationMetro, StationTramway) (requis)
            adresse: Adresse de la station (optionnel)
            latitude: Latitude GPS (optionnel)
            longitude: Longitude GPS (optionnel)
            ville_uri: URI de la ville où se situe la station (optionnel)
            
        Returns:
            bool: True si succès, False sinon
        """
        # Générer un URI unique pour la station
        uri_safe_nom = nom.replace(" ", "_").replace("'", "").replace("-", "_")
        station_uri = f"{self.TRANSPORT_PREFIX}Station_{uri_safe_nom}"
        
        # Construire la requête INSERT
        insert_query = f"""
INSERT DATA {{
    <{station_uri}> rdf:type transport:Station ;
                    rdf:type transport:{type_station} ;
                    transport:nom "{nom}" .
"""
        
        # Ajouter les propriétés optionnelles
        if adresse:
            insert_query += f'    <{station_uri}> transport:adresse "{adresse}" .\n'
        
        if latitude is not None:
            insert_query += f'    <{station_uri}> transport:latitude "{latitude}"^^xsd:float .\n'
        
        if longitude is not None:
            insert_query += f'    <{station_uri}> transport:longitude "{longitude}"^^xsd:float .\n'
        
        if ville_uri:
            insert_query += f'    <{station_uri}> transport:situeDans <{ville_uri}> .\n'
        
        insert_query += "}"
        
        return self.execute_update(insert_query)
    
    def delete_station(self, station_uri: str) -> bool:
        """Supprime une station de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{station_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_station(self, station_uri: str, nom: str = None, adresse: str = None,
                      latitude: float = None, longitude: float = None) -> bool:
        """
        Met à jour une station existante
        
        Args:
            station_uri: URI de la station à mettre à jour
            nom: Nouveau nom (optionnel)
            adresse: Nouvelle adresse (optionnel)
            latitude: Nouvelle latitude (optionnel)
            longitude: Nouvelle longitude (optionnel)
            
        Returns:
            bool: True si succès, False sinon
        """
        if not any([nom, adresse, latitude is not None, longitude is not None]):
            return True
        
        # Construire la requête DELETE/INSERT
        update_query = f"""
DELETE {{
    <{station_uri}> transport:nom ?oldNom ;
                    transport:adresse ?oldAdresse ;
                    transport:latitude ?oldLat ;
                    transport:longitude ?oldLong .
}}
INSERT {{
"""
        
        if nom:
            update_query += f'    <{station_uri}> transport:nom "{nom}" .\n'
        if adresse:
            update_query += f'    <{station_uri}> transport:adresse "{adresse}" .\n'
        if latitude is not None:
            update_query += f'    <{station_uri}> transport:latitude "{latitude}"^^xsd:float .\n'
        if longitude is not None:
            update_query += f'    <{station_uri}> transport:longitude "{longitude}"^^xsd:float .\n'
        
        update_query += f"""
}}
WHERE {{
    <{station_uri}> rdf:type ?type .
    OPTIONAL {{ <{station_uri}> transport:nom ?oldNom }}
    OPTIONAL {{ <{station_uri}> transport:adresse ?oldAdresse }}
    OPTIONAL {{ <{station_uri}> transport:latitude ?oldLat }}
    OPTIONAL {{ <{station_uri}> transport:longitude ?oldLong }}
}}
"""
        
        return self.execute_update(update_query)
    
    def get_all_villes(self) -> List[Dict]:
        """Récupère toutes les villes pour les dropdowns"""
        query = """
SELECT ?ville ?nom
WHERE {
    ?ville rdf:type transport:Ville .
    OPTIONAL { ?ville transport:nom ?nom }
}
ORDER BY ?nom
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

