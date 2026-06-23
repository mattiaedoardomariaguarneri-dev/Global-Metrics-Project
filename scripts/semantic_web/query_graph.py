import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)

def run_all_queries():
    print("=========================================================")
    print("[INFO] Avvio del motore SPARQL Locale...")
    print("=========================================================")
    g = rdflib.Graph()
    g.parse("processed/rdf/global_metrics.ttl", format="turtle")
    print(f"[SUCCESS] Grafo caricato! Triple in memoria: {len(g)}\n")

    # ------------------------------------------------------------------
    # QUERY 1: GLI "HEAVY EMITTERS"
    # ------------------------------------------------------------------
    print("\n>>> QUERY 1: Gli 'Heavy Emitters' (GDP > 40.000$, Densità > 200)")
    q1 = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?countryName ?gdp ?density ?co2
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasGDPPerCapita ?gdp ;
                 gmont:hasPopulationDensity ?density ;
                 gmont:hasCO2Emissions ?co2 .
                 
        FILTER (?gdp > 40000 && ?density > 200)
    }
    ORDER BY DESC(?co2)
    """
    res1 = g.query(q1)
    print(f"{'PAESE':<20} | {'GDP ($)':<10} | {'DENSITA (ppl/kmq)':<18} | {'CO2 (ton/cap)':<13}")
    print("-" * 68)
    for r in res1:
        print(f"{str(r.countryName):<20} | {float(r.gdp):<10.0f} | {float(r.density):<18.2f} | {float(r.co2):<13.2f}")


    # ------------------------------------------------------------------
    # QUERY 2: I "PAESI PARADISO" (Dal Markdown Originale)
    # ------------------------------------------------------------------
    print("\n>>> QUERY 2: I Paesi 'Paradiso' Rigorosi (GDP > 30.000$, CO2 < 5 tonnellate)")
    q2 = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?countryName ?gdp ?co2
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasGDPPerCapita ?gdp ;
                 gmont:hasCO2Emissions ?co2 .
                 
        FILTER (?gdp > 30000 && ?co2 < 5.0)
    }
    ORDER BY ASC(?co2)
    """
    res2 = g.query(q2)
    print(f"{'PAESE':<20} | {'GDP ($)':<10} | {'CO2 (ton/cap)':<13}")
    print("-" * 48)
    count = 0
    for r in res2:
        count += 1
        print(f"{str(r.countryName):<20} | {float(r.gdp):<10.0f} | {float(r.co2):<13.2f}")
    if count == 0:
        print("Nessun paese soddisfa questo standard ambientale severissimo!")


    # ------------------------------------------------------------------
    # QUERY 3: I "RICCHI MA VERDI" (Rilassata)
    # ------------------------------------------------------------------
    print("\n>>> QUERY 3: I Paesi 'Ricchi ma Verdi' (GDP > 50.000$, CO2 < 40 tonnellate)")
    q3 = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?countryName ?gdp ?co2
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasGDPPerCapita ?gdp ;
                 gmont:hasCO2Emissions ?co2 .
                 
        FILTER (?gdp > 50000 && ?co2 < 40.0)
    }
    ORDER BY ASC(?co2)
    """
    res3 = g.query(q3)
    print(f"{'PAESE':<20} | {'GDP ($)':<10} | {'CO2 (ton/cap)':<13}")
    print("-" * 48)
    for r in res3:
        print(f"{str(r.countryName):<20} | {float(r.gdp):<10.0f} | {float(r.co2):<13.2f}")


    # ------------------------------------------------------------------
    # QUERY 4: IL DIVIDENDO DELLA LONGEVITA'
    # ------------------------------------------------------------------
    print("\n>>> QUERY 4: Il Dividendo della Longevità (Aspettativa di vita dell'élite globale, GDP > 50.000$)")
    q4 = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?countryName ?gdp ?lifeExpectancy
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasGDPPerCapita ?gdp ;
                 gmont:hasLifeExpectancy ?lifeExpectancy .
                 
        FILTER (?gdp > 50000)
    }
    ORDER BY DESC(?lifeExpectancy)
    """
    res4 = g.query(q4)
    print(f"{'PAESE':<20} | {'GDP ($)':<10} | {'VITA (anni)':<13}")
    print("-" * 48)
    for r in res4:
        print(f"{str(r.countryName):<20} | {float(r.gdp):<10.0f} | {float(r.lifeExpectancy):<13.1f}")


    # ------------------------------------------------------------------
    # QUERY 5: FEDERATED QUERYING SU DBPEDIA
    # ------------------------------------------------------------------
    print("\n>>> QUERY 5: Federated Query su DBpedia (Trova le capitali dei Paesi con Aspettativa di vita > 82)")
    print("[ATTENZIONE] Utilizzo di SPARQLWrapper per bypassare l'Errore 406...")
    
    # 1. Troviamo i paesi nel nostro grafo locale
    q5_local = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?countryName ?lifeExpectancy ?dbpediaURI
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasLifeExpectancy ?lifeExpectancy ;
                 gmont:exactMatchDBpedia ?dbpediaURI .
        FILTER (?lifeExpectancy > 82)
    }
    ORDER BY DESC(?lifeExpectancy)
    """
    res5_local = list(g.query(q5_local))
    
    print(f"{'PAESE':<20} | {'VITA (anni)':<13} | {'CAPITALE (DBpedia)':<20}")
    print("-" * 60)
    
    # Inizializziamo SPARQLWrapper per DBpedia
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    
    # 2. Per ognuno, chiediamo la capitale a DBpedia tramite rete (Federazione manuale a 2 step)
    for r in res5_local:
        country_name = str(r.countryName)
        life_exp = float(r.lifeExpectancy)
        dbp_uri = str(r.dbpediaURI)
        
        dbp_query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?capitalName WHERE {{
            <{dbp_uri}> dbo:capital ?capitalURI .
            ?capitalURI rdfs:label ?capitalName .
            FILTER (lang(?capitalName) = 'en')
        }} LIMIT 1
        """
        sparql.setQuery(dbp_query)
        try:
            results = sparql.query().convert()
            bindings = results["results"]["bindings"]
            capital_name = bindings[0]["capitalName"]["value"] if bindings else "N/D"
        except Exception as e:
            capital_name = f"Errore connessione: {e}"
            
        print(f"{country_name:<20} | {life_exp:<13.1f} | {capital_name:<20}")

    # ------------------------------------------------------------------
    # QUERY 6: L'INTERSEZIONE MONETARIA (Federated su Heavy Emitters)
    # ------------------------------------------------------------------
    print("\n>>> QUERY 6: Federated Query (Valuta ufficiale dei top inquinatori 'Heavy Emitters')")
    
    q6_local = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?countryName ?co2 ?dbpediaURI
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasGDPPerCapita ?gdp ;
                 gmont:hasPopulationDensity ?density ;
                 gmont:hasCO2Emissions ?co2 ;
                 gmont:exactMatchDBpedia ?dbpediaURI .
        FILTER (?gdp > 40000 && ?density > 200)
    }
    ORDER BY DESC(?co2)
    """
    res6_local = list(g.query(q6_local))
    print(f"{'PAESE':<20} | {'CO2':<10} | {'VALUTA (DBpedia)':<30}")
    print("-" * 65)
    for r in res6_local:
        dbp_query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?currencyName WHERE {{
            <{r.dbpediaURI}> dbo:currency ?currencyURI .
            ?currencyURI rdfs:label ?currencyName .
            FILTER (lang(?currencyName) = 'en')
        }} LIMIT 1
        """
        sparql.setQuery(dbp_query)
        try:
            results = sparql.query().convert()
            b = results["results"]["bindings"]
            currency = b[0]["currencyName"]["value"] if b else "N/D"
        except:
            currency = "Errore HTTP"
        print(f"{str(r.countryName):<20} | {float(r.co2):<10.2f} | {currency:<30}")

    # ------------------------------------------------------------------
    # QUERY 7: LA LINGUA DEI LONGEVI (Federated)
    # ------------------------------------------------------------------
    print("\n>>> QUERY 7: Federated Query (Lingua ufficiale nei Paesi con Aspettativa di vita > 83)")
    q7_local = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?countryName ?life ?dbpediaURI
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasLifeExpectancy ?life ;
                 gmont:exactMatchDBpedia ?dbpediaURI .
        FILTER (?life > 83.0)
    }
    ORDER BY DESC(?life)
    """
    res7_local = list(g.query(q7_local))
    print(f"{'PAESE':<20} | {'VITA':<10} | {'LINGUA (DBpedia)':<30}")
    print("-" * 65)
    for r in res7_local:
        dbp_query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?langName WHERE {{
            <{r.dbpediaURI}> dbo:language ?langURI .
            ?langURI rdfs:label ?langName .
            FILTER (lang(?langName) = 'en')
        }} LIMIT 1
        """
        sparql.setQuery(dbp_query)
        try:
            results = sparql.query().convert()
            b = results["results"]["bindings"]
            language = b[0]["langName"]["value"] if b else "N/D"
        except:
            language = "Errore HTTP"
            
        # Fix encoding issues for Windows terminals
        safe_language = language.encode('cp1252', errors='replace').decode('cp1252')
        print(f"{str(r.countryName):<20} | {float(r.life):<10.1f} | {safe_language:<30}")

    print("\n[INFO] Esecuzione delle query completata.")

if __name__ == "__main__":
    run_all_queries()
