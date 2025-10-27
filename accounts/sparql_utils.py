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
    
    # ===== MÉTHODES CRUD POUR LES HORAIRES =====
    
    def get_horaires(self) -> List[Dict]:
        """Récupère tous les horaires"""
        query = """
SELECT ?horaire ?heureDepart ?heureArrivee ?jour ?type
WHERE {
    ?horaire rdf:type/rdfs:subClassOf* transport:Horaire .
    OPTIONAL { ?horaire transport:heureDepart ?heureDepart }
    OPTIONAL { ?horaire transport:heureArrivee ?heureArrivee }
    OPTIONAL { ?horaire transport:jour ?jour }
    OPTIONAL { 
        ?horaire rdf:type ?type .
        FILTER (?type != transport:Horaire)
    }
}
ORDER BY ?jour ?heureDepart
"""
        return self.execute_query(query)
    
    def create_horaire(self, heureDepart: str, heureArrivee: str, jour: str = None, type_horaire: str = "Horaire") -> bool:
        """Crée un nouvel horaire dans l'ontologie"""
        import uuid
        horaire_id = str(uuid.uuid4())[:8]
        horaire_uri = f"{self.TRANSPORT_PREFIX}Horaire_{horaire_id}"
        
        insert_query = f"""
INSERT DATA {{
    <{horaire_uri}> rdf:type transport:Horaire ;
                    rdf:type transport:{type_horaire} ;
                    transport:heureDepart "{heureDepart}" ;
                    transport:heureArrivee "{heureArrivee}" .
"""
        if jour:
            insert_query += f'    <{horaire_uri}> transport:jour "{jour}" .\n'
        
        insert_query += "}"
        return self.execute_update(insert_query)
    
    def delete_horaire(self, horaire_uri: str) -> bool:
        """Supprime un horaire de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{horaire_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_horaire(self, horaire_uri: str, heureDepart: str = None, heureArrivee: str = None, jour: str = None) -> bool:
        """Met à jour un horaire existant"""
        if not any([heureDepart is not None, heureArrivee is not None, jour is not None]):
            return True
        
        update_query = f"""
DELETE {{
    <{horaire_uri}> transport:heureDepart ?oldDepart ;
                    transport:heureArrivee ?oldArrivee ;
                    transport:jour ?oldJour .
}}
INSERT {{
"""
        if heureDepart is not None:
            update_query += f'    <{horaire_uri}> transport:heureDepart "{heureDepart}" .\n'
        if heureArrivee is not None:
            update_query += f'    <{horaire_uri}> transport:heureArrivee "{heureArrivee}" .\n'
        if jour is not None:
            update_query += f'    <{horaire_uri}> transport:jour "{jour}" .\n'
        
        update_query += f"""
}}
WHERE {{
    <{horaire_uri}> rdf:type ?type .
    OPTIONAL {{ <{horaire_uri}> transport:heureDepart ?oldDepart }}
    OPTIONAL {{ <{horaire_uri}> transport:heureArrivee ?oldArrivee }}
    OPTIONAL {{ <{horaire_uri}> transport:jour ?oldJour }}
}}
"""
        return self.execute_update(update_query)
    
    # ===== MÉTHODES CRUD POUR LES PARKINGS =====
    
    def get_parkings(self) -> List[Dict]:
        """Récupère tous les parkings"""
        query = """
SELECT ?parking ?nom ?nombrePlaces ?placesDisponibles ?adresse ?latitude ?longitude ?type
WHERE {
    ?parking rdf:type/rdfs:subClassOf* transport:Parking .
    OPTIONAL { ?parking transport:nom ?nom }
    OPTIONAL { ?parking transport:nombrePlaces ?nombrePlaces }
    OPTIONAL { ?parking transport:placesDisponibles ?placesDisponibles }
    OPTIONAL { ?parking transport:adresse ?adresse }
    OPTIONAL { ?parking transport:latitude ?latitude }
    OPTIONAL { ?parking transport:longitude ?longitude }
    OPTIONAL { 
        ?parking rdf:type ?type .
        FILTER (?type != transport:Parking)
    }
}
ORDER BY ?nom
"""
        return self.execute_query(query)
    
    def create_parking(self, nom: str, nombrePlaces: int, placesDisponibles: int = None, 
                       adresse: str = None, latitude: float = None, longitude: float = None,
                       type_parking: str = "Parking") -> bool:
        """Crée un nouveau parking dans l'ontologie"""
        uri_safe_nom = nom.replace(" ", "_").replace("'", "")
        parking_uri = f"{self.TRANSPORT_PREFIX}Parking_{uri_safe_nom}"
        
        insert_query = f"""
INSERT DATA {{
    <{parking_uri}> rdf:type transport:Parking ;
                    rdf:type transport:{type_parking} ;
                    transport:nom "{nom}" ;
                    transport:nombrePlaces "{nombrePlaces}"^^xsd:integer .
"""
        if placesDisponibles is not None:
            insert_query += f'    <{parking_uri}> transport:placesDisponibles "{placesDisponibles}"^^xsd:integer .\n'
        if adresse:
            insert_query += f'    <{parking_uri}> transport:adresse "{adresse}" .\n'
        if latitude is not None:
            insert_query += f'    <{parking_uri}> transport:latitude "{latitude}"^^xsd:float .\n'
        if longitude is not None:
            insert_query += f'    <{parking_uri}> transport:longitude "{longitude}"^^xsd:float .\n'
        
        insert_query += "}"
        return self.execute_update(insert_query)
    
    def delete_parking(self, parking_uri: str) -> bool:
        """Supprime un parking de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{parking_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_parking(self, parking_uri: str, nom: str = None, nombrePlaces: int = None,
                       placesDisponibles: int = None, adresse: str = None) -> bool:
        """Met à jour un parking existant"""
        if not any([nom is not None, nombrePlaces is not None, placesDisponibles is not None, adresse is not None]):
            return True
        
        update_query = f"""
DELETE {{
    <{parking_uri}> transport:nom ?oldNom ;
                    transport:nombrePlaces ?oldNbPlaces ;
                    transport:placesDisponibles ?oldPlacesDispo ;
                    transport:adresse ?oldAdresse .
}}
INSERT {{
"""
        if nom is not None:
            update_query += f'    <{parking_uri}> transport:nom "{nom}" .\n'
        if nombrePlaces is not None:
            update_query += f'    <{parking_uri}> transport:nombrePlaces "{nombrePlaces}"^^xsd:integer .\n'
        if placesDisponibles is not None:
            update_query += f'    <{parking_uri}> transport:placesDisponibles "{placesDisponibles}"^^xsd:integer .\n'
        if adresse is not None:
            update_query += f'    <{parking_uri}> transport:adresse "{adresse}" .\n'
        
        update_query += f"""
}}
WHERE {{
    <{parking_uri}> rdf:type ?type .
    OPTIONAL {{ <{parking_uri}> transport:nom ?oldNom }}
    OPTIONAL {{ <{parking_uri}> transport:nombrePlaces ?oldNbPlaces }}
    OPTIONAL {{ <{parking_uri}> transport:placesDisponibles ?oldPlacesDispo }}
    OPTIONAL {{ <{parking_uri}> transport:adresse ?oldAdresse }}
}}
"""
        return self.execute_update(update_query)
    
    # ===== MÉTHODES CRUD POUR LES ÉVÉNEMENTS =====
    
    def get_evenements(self) -> List[Dict]:
        """Récupère tous les événements de trafic"""
        query = """
SELECT ?evenement ?typeEvenement ?dateEvenement ?description ?latitude ?longitude ?type
WHERE {
    ?evenement rdf:type/rdfs:subClassOf* transport:ÉvénementTrafic .
    OPTIONAL { ?evenement transport:typeEvenement ?typeEvenement }
    OPTIONAL { ?evenement transport:dateEvenement ?dateEvenement }
    OPTIONAL { ?evenement transport:description ?description }
    OPTIONAL { ?evenement transport:latitude ?latitude }
    OPTIONAL { ?evenement transport:longitude ?longitude }
    OPTIONAL { 
        ?evenement rdf:type ?type .
        FILTER (?type != transport:ÉvénementTrafic)
    }
}
ORDER BY DESC(?dateEvenement)
"""
        return self.execute_query(query)
    
    def create_evenement(self, typeEvenement: str, dateEvenement: str = None, 
                         description: str = None, latitude: float = None, 
                         longitude: float = None, type_evt: str = "ÉvénementTrafic") -> bool:
        """Crée un nouvel événement de trafic dans l'ontologie"""
        import uuid
        evt_id = str(uuid.uuid4())[:8]
        evt_uri = f"{self.TRANSPORT_PREFIX}Evenement_{evt_id}"
        
        insert_query = f"""
INSERT DATA {{
    <{evt_uri}> rdf:type transport:ÉvénementTrafic ;
                rdf:type transport:{type_evt} ;
                transport:typeEvenement "{typeEvenement}" .
"""
        if dateEvenement:
            insert_query += f'    <{evt_uri}> transport:dateEvenement "{dateEvenement}" .\n'
        if description:
            insert_query += f'    <{evt_uri}> transport:description "{description}" .\n'
        if latitude is not None:
            insert_query += f'    <{evt_uri}> transport:latitude "{latitude}"^^xsd:float .\n'
        if longitude is not None:
            insert_query += f'    <{evt_uri}> transport:longitude "{longitude}"^^xsd:float .\n'
        
        insert_query += "}"
        return self.execute_update(insert_query)
    
    def delete_evenement(self, evenement_uri: str) -> bool:
        """Supprime un événement de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{evenement_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_evenement(self, evenement_uri: str, typeEvenement: str = None,
                         dateEvenement: str = None, description: str = None) -> bool:
        """Met à jour un événement existant"""
        if not any([typeEvenement is not None, dateEvenement is not None, description is not None]):
            return True
        
        update_query = f"""
DELETE {{
    <{evenement_uri}> transport:typeEvenement ?oldType ;
                      transport:dateEvenement ?oldDate ;
                      transport:description ?oldDesc .
}}
INSERT {{
"""
        if typeEvenement is not None:
            update_query += f'    <{evenement_uri}> transport:typeEvenement "{typeEvenement}" .\n'
        if dateEvenement is not None:
            update_query += f'    <{evenement_uri}> transport:dateEvenement "{dateEvenement}" .\n'
        if description is not None:
            update_query += f'    <{evenement_uri}> transport:description "{description}" .\n'
        
        update_query += f"""
}}
WHERE {{
    <{evenement_uri}> rdf:type ?type .
    OPTIONAL {{ <{evenement_uri}> transport:typeEvenement ?oldType }}
    OPTIONAL {{ <{evenement_uri}> transport:dateEvenement ?oldDate }}
    OPTIONAL {{ <{evenement_uri}> transport:description ?oldDesc }}
}}
"""
        return self.execute_update(update_query)
    
    # ===== MÉTHODES CRUD POUR LES CAPTEURS =====
    
    def get_capteurs(self) -> List[Dict]:
        """Récupère tous les capteurs"""
        query = """
SELECT ?capteur ?nom ?etat ?type ?latitude ?longitude
WHERE {
    ?capteur rdf:type/rdfs:subClassOf* transport:Capteur .
    OPTIONAL { ?capteur transport:nom ?nom }
    OPTIONAL { ?capteur transport:etat ?etat }
    OPTIONAL { ?capteur transport:latitude ?latitude }
    OPTIONAL { ?capteur transport:longitude ?longitude }
    OPTIONAL { 
        ?capteur rdf:type ?type .
        FILTER (?type != transport:Capteur)
    }
}
ORDER BY ?nom
"""
        return self.execute_query(query)
    
    def create_capteur(self, nom: str, type_capteur: str, etat: str = None,
                       latitude: float = None, longitude: float = None) -> bool:
        """Crée un nouveau capteur dans l'ontologie"""
        uri_safe_nom = nom.replace(" ", "_").replace("'", "")
        capteur_uri = f"{self.TRANSPORT_PREFIX}Capteur_{uri_safe_nom}"
        
        insert_query = f"""
INSERT DATA {{
    <{capteur_uri}> rdf:type transport:Capteur ;
                    rdf:type transport:{type_capteur} ;
                    transport:nom "{nom}" .
"""
        if etat:
            insert_query += f'    <{capteur_uri}> transport:etat "{etat}" .\n'
        if latitude is not None:
            insert_query += f'    <{capteur_uri}> transport:latitude "{latitude}"^^xsd:float .\n'
        if longitude is not None:
            insert_query += f'    <{capteur_uri}> transport:longitude "{longitude}"^^xsd:float .\n'
        
        insert_query += "}"
        return self.execute_update(insert_query)
    
    def delete_capteur(self, capteur_uri: str) -> bool:
        """Supprime un capteur de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{capteur_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_capteur(self, capteur_uri: str, nom: str = None, etat: str = None) -> bool:
        """Met à jour un capteur existant"""
        if not any([nom is not None, etat is not None]):
            return True
        
        update_query = f"""
DELETE {{
    <{capteur_uri}> transport:nom ?oldNom ;
                    transport:etat ?oldEtat .
}}
INSERT {{
"""
        if nom is not None:
            update_query += f'    <{capteur_uri}> transport:nom "{nom}" .\n'
        if etat is not None:
            update_query += f'    <{capteur_uri}> transport:etat "{etat}" .\n'
        
        update_query += f"""
}}
WHERE {{
    <{capteur_uri}> rdf:type ?type .
    OPTIONAL {{ <{capteur_uri}> transport:nom ?oldNom }}
    OPTIONAL {{ <{capteur_uri}> transport:etat ?oldEtat }}
}}
"""
        return self.execute_update(update_query)
    
    # ===== MÉTHODES CRUD POUR LES ROUTES =====
    
    def get_routes(self) -> List[Dict]:
        """Récupère toutes les routes"""
        query = """
SELECT ?route ?nom ?longueur ?etatRoute ?type
WHERE {
    ?route rdf:type/rdfs:subClassOf* transport:Route .
    OPTIONAL { ?route transport:nom ?nom }
    OPTIONAL { ?route transport:longueur ?longueur }
    OPTIONAL { ?route transport:etatRoute ?etatRoute }
    OPTIONAL { 
        ?route rdf:type ?type .
        FILTER (?type != transport:Route)
    }
}
ORDER BY ?nom
"""
        return self.execute_query(query)
    
    def create_route(self, nom: str, type_route: str, longueur: float = None, 
                     etatRoute: str = None) -> bool:
        """Crée une nouvelle route dans l'ontologie"""
        uri_safe_nom = nom.replace(" ", "_").replace("'", "")
        route_uri = f"{self.TRANSPORT_PREFIX}Route_{uri_safe_nom}"
        
        insert_query = f"""
INSERT DATA {{
    <{route_uri}> rdf:type transport:Route ;
                  rdf:type transport:{type_route} ;
                  transport:nom "{nom}" .
"""
        if longueur is not None:
            insert_query += f'    <{route_uri}> transport:longueur "{longueur}"^^xsd:float .\n'
        if etatRoute:
            insert_query += f'    <{route_uri}> transport:etatRoute "{etatRoute}" .\n'
        
        insert_query += "}"
        return self.execute_update(insert_query)
    
    def delete_route(self, route_uri: str) -> bool:
        """Supprime une route de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{route_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_route(self, route_uri: str, nom: str = None, longueur: float = None, 
                     etatRoute: str = None) -> bool:
        """Met à jour une route existante"""
        if not any([nom is not None, longueur is not None, etatRoute is not None]):
            return True
        
        update_query = f"""
DELETE {{
    <{route_uri}> transport:nom ?oldNom ;
                  transport:longueur ?oldLongueur ;
                  transport:etatRoute ?oldEtat .
}}
INSERT {{
"""
        if nom is not None:
            update_query += f'    <{route_uri}> transport:nom "{nom}" .\n'
        if longueur is not None:
            update_query += f'    <{route_uri}> transport:longueur "{longueur}"^^xsd:float .\n'
        if etatRoute is not None:
            update_query += f'    <{route_uri}> transport:etatRoute "{etatRoute}" .\n'
        
        update_query += f"""
}}
WHERE {{
    <{route_uri}> rdf:type ?type .
    OPTIONAL {{ <{route_uri}> transport:nom ?oldNom }}
    OPTIONAL {{ <{route_uri}> transport:longueur ?oldLongueur }}
    OPTIONAL {{ <{route_uri}> transport:etatRoute ?oldEtat }}
}}
"""
        return self.execute_update(update_query)
    
    # ===== MÉTHODES CRUD POUR LES VILLES =====
    
    def get_villes(self) -> List[Dict]:
        """Récupère toutes les villes"""
        query = """
SELECT ?ville ?nom ?latitude ?longitude ?type
WHERE {
    ?ville rdf:type/rdfs:subClassOf* transport:Ville .
    OPTIONAL { ?ville transport:nom ?nom }
    OPTIONAL { ?ville transport:latitude ?latitude }
    OPTIONAL { ?ville transport:longitude ?longitude }
    OPTIONAL { 
        ?ville rdf:type ?type .
        FILTER (?type != transport:Ville)
    }
}
ORDER BY ?nom
"""
        return self.execute_query(query)
    
    def create_ville(self, nom: str, type_ville: str = "Ville", 
                     latitude: float = None, longitude: float = None) -> bool:
        """Crée une nouvelle ville dans l'ontologie"""
        uri_safe_nom = nom.replace(" ", "_").replace("'", "")
        ville_uri = f"{self.TRANSPORT_PREFIX}Ville_{uri_safe_nom}"
        
        insert_query = f"""
INSERT DATA {{
    <{ville_uri}> rdf:type transport:Ville ;
                  rdf:type transport:{type_ville} ;
                  transport:nom "{nom}" .
"""
        if latitude is not None:
            insert_query += f'    <{ville_uri}> transport:latitude "{latitude}"^^xsd:float .\n'
        if longitude is not None:
            insert_query += f'    <{ville_uri}> transport:longitude "{longitude}"^^xsd:float .\n'
        
        insert_query += "}"
        return self.execute_update(insert_query)
    
    def delete_ville(self, ville_uri: str) -> bool:
        """Supprime une ville de l'ontologie"""
        delete_query = f"""
DELETE WHERE {{
    <{ville_uri}> ?p ?o .
}}
"""
        return self.execute_update(delete_query)
    
    def update_ville(self, ville_uri: str, nom: str = None, 
                     latitude: float = None, longitude: float = None) -> bool:
        """Met à jour une ville existante"""
        if not any([nom is not None, latitude is not None, longitude is not None]):
            return True
        
        update_query = f"""
DELETE {{
    <{ville_uri}> transport:nom ?oldNom ;
                  transport:latitude ?oldLat ;
                  transport:longitude ?oldLon .
}}
INSERT {{
"""
        if nom is not None:
            update_query += f'    <{ville_uri}> transport:nom "{nom}" .\n'
        if latitude is not None:
            update_query += f'    <{ville_uri}> transport:latitude "{latitude}"^^xsd:float .\n'
        if longitude is not None:
            update_query += f'    <{ville_uri}> transport:longitude "{longitude}"^^xsd:float .\n'
        
        update_query += f"""
}}
WHERE {{
    <{ville_uri}> rdf:type ?type .
    OPTIONAL {{ <{ville_uri}> transport:nom ?oldNom }}
    OPTIONAL {{ <{ville_uri}> transport:latitude ?oldLat }}
    OPTIONAL {{ <{ville_uri}> transport:longitude ?oldLon }}
}}
"""
        return self.execute_update(update_query)


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

