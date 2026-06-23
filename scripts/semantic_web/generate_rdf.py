import json
import logging
import os
from pathlib import Path

# Fix per percorsi relativi: ci posizioniamo nella root del progetto
PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)
from pathlib import Path

import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, XSD, OWL, DCAT, DCTERMS

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("rdf_generator")

def generate_rdf_and_queries():
    import os
    os.makedirs("processed/rdf", exist_ok=True)
    logger.info("Loading processed dataset...")
    df = pd.read_csv("processed/csv/global_metrics_2020.csv")
    
    # Define Namespaces
    GM_RES = Namespace("http://globalmetrics.org/resource/")
    GM_ONT = Namespace("http://globalmetrics.org/ontology/")
    DBPEDIA = Namespace("http://dbpedia.org/resource/")
    
    g = Graph()
    g.bind("gmres", GM_RES)
    g.bind("gmont", GM_ONT)
    g.bind("dbpedia", DBPEDIA)
    g.bind("owl", OWL)
    g.bind("dcat", DCAT)
    g.bind("dcterms", DCTERMS)
    
    # Graph for Ontology (T-Box)
    g_ont = Graph()
    g_ont.bind("gmont", GM_ONT)
    g_ont.bind("owl", OWL)
    g_ont.bind("rdfs", RDFS)
    g_ont.bind("xsd", XSD)
    
    SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
    PROV = Namespace("http://www.w3.org/ns/prov#")
    QUDT = Namespace("http://qudt.org/schema/qudt/")
    g_ont.bind("skos", SKOS)
    g_ont.bind("prov", PROV)
    g_ont.bind("qudt", QUDT)
    g_ont.bind("dcterms", DCTERMS)
    
    # Define Ontology Classes and Properties
    ont_uri = GM_ONT[""]
    g_ont.add((ont_uri, RDF.type, OWL.Ontology))
    g_ont.add((ont_uri, RDFS.label, Literal("Global Metrics Ontology", lang="en")))
    g_ont.add((ont_uri, DCTERMS.description, Literal("An ontology to describe global metrics like GDP, Population Density, Life Expectancy, and CO2 emissions for countries.", lang="en")))
    g_ont.add((ont_uri, RDFS.comment, Literal("A structured vocabulary for Global Metrics. It defines the Country class, its Data Properties (indicators), and Object Properties for interlinking.", lang="en")))
    g_ont.add((ont_uri, OWL.versionInfo, Literal("1.1", lang="en")))

    # --- Classes ---
    g_ont.add((GM_ONT.Country, RDF.type, OWL.Class))
    g_ont.add((GM_ONT.Country, RDFS.label, Literal("Country", lang="en")))
    g_ont.add((GM_ONT.Country, SKOS.prefLabel, Literal("Country", lang="en")))
    g_ont.add((GM_ONT.Country, RDFS.comment, Literal("A sovereign state, nation, or territory.", lang="en")))
    g_ont.add((GM_ONT.Country, SKOS.definition, Literal("A distinct territorial body or political entity.", lang="en")))
    g_ont.add((GM_ONT.Country, RDFS.isDefinedBy, ont_uri))

    # --- Object Properties ---
    g_ont.add((GM_ONT.exactMatchDBpedia, RDF.type, OWL.ObjectProperty))
    g_ont.add((GM_ONT.exactMatchDBpedia, RDFS.subPropertyOf, OWL.sameAs))
    g_ont.add((GM_ONT.exactMatchDBpedia, RDFS.label, Literal("exact match DBpedia", lang="en")))
    g_ont.add((GM_ONT.exactMatchDBpedia, RDFS.comment, Literal("Links the Country to its corresponding DBpedia resource.", lang="en")))
    g_ont.add((GM_ONT.exactMatchDBpedia, RDFS.domain, GM_ONT.Country))
    g_ont.add((GM_ONT.exactMatchDBpedia, RDFS.isDefinedBy, ont_uri))

    # --- Datatype Properties ---
    wb_source = URIRef("https://data.worldbank.org/")
    
    props = {
        GM_ONT.hasPopulationDensity: {
            "label": "has population density",
            "prefLabel": "Population Density",
            "notation": "POP_DENS",
            "comment": "The population density (people per sq. km).",
            "scopeNote": "Calculated as total population divided by land area.",
            "source": URIRef("https://data.worldbank.org/indicator/EN.POP.DNST"),
            "unit": "People per sq. km",
            "range": XSD.float
        },
        GM_ONT.hasGDPPerCapita: {
            "label": "has GDP per capita",
            "prefLabel": "GDP per capita (US$)",
            "notation": "GDP_PC",
            "comment": "The Gross Domestic Product per capita in current US dollars.",
            "scopeNote": "GDP divided by midyear population.",
            "source": URIRef("https://data.worldbank.org/indicator/NY.GDP.PCAP.CD"),
            "unit": "Current US$",
            "range": XSD.float
        },
        GM_ONT.hasLifeExpectancy: {
            "label": "has life expectancy",
            "prefLabel": "Life Expectancy at Birth",
            "notation": "LIFE_EXP",
            "comment": "The life expectancy at birth, total (years).",
            "scopeNote": "Indicates the number of years a newborn infant would live if prevailing patterns of mortality at the time of its birth were to stay the same.",
            "source": URIRef("https://data.worldbank.org/indicator/SP.DYN.LE00.IN"),
            "unit": "Years",
            "range": XSD.float
        },
        GM_ONT.hasCO2Emissions: {
            "label": "has CO2 emissions",
            "prefLabel": "CO2 Emissions per capita",
            "notation": "CO2_PC",
            "comment": "The CO2 emissions (metric tons per capita).",
            "scopeNote": "Emissions stemming from the burning of fossil fuels and the manufacture of cement.",
            "source": URIRef("https://data.worldbank.org/indicator/EN.ATM.CO2E.PC"),
            "unit": "Metric tons per capita",
            "range": XSD.float
        }
    }

    for prop, p_data in props.items():
        g_ont.add((prop, RDF.type, OWL.DatatypeProperty))
        g_ont.add((prop, RDFS.label, Literal(p_data["label"], lang="en")))
        g_ont.add((prop, SKOS.prefLabel, Literal(p_data["prefLabel"], lang="en")))
        g_ont.add((prop, SKOS.notation, Literal(p_data["notation"])))
        g_ont.add((prop, RDFS.comment, Literal(p_data["comment"], lang="en")))
        g_ont.add((prop, SKOS.scopeNote, Literal(p_data["scopeNote"], lang="en")))
        g_ont.add((prop, RDFS.domain, GM_ONT.Country))
        g_ont.add((prop, RDFS.range, p_data["range"]))
        g_ont.add((prop, RDFS.isDefinedBy, ont_uri))
        g_ont.add((prop, PROV.wasDerivedFrom, p_data["source"]))
        g_ont.add((prop, DCTERMS.date, Literal("2020", datatype=XSD.gYear)))
        g_ont.add((prop, QUDT.unit, Literal(p_data["unit"], lang="en")))
    
    # Save Ontology
    ont_path = "processed/rdf/ontology.ttl"
    g_ont.serialize(destination=ont_path, format="turtle")
    logger.info(f"Ontology Schema (T-Box) saved to {ont_path} for Protégé.")
    
    logger.info("Building Knowledge Graph (A-Box)...")
    
    # Merge T-Box into A-Box so the final global_metrics.ttl contains both schema and instances
    g += g_ont
    
    for _, row in df.iterrows():
        country_code = str(row["country_code"])
        country_name = str(row["country_name"])
        dbpedia_uri = str(row["dbpedia_uri"])
        
        # URI fittizia per la risorsa Paese
        country_uri = GM_RES[country_code]
        
        g.add((country_uri, RDF.type, GM_ONT.Country))
        g.add((country_uri, RDFS.label, Literal(country_name, lang="en")))
        
        # 5-star open data: Interlinking to DBpedia
        if pd.notna(dbpedia_uri):
            # Use our custom Object Property (which is a subProperty of owl:sameAs)
            g.add((country_uri, GM_ONT.exactMatchDBpedia, URIRef(dbpedia_uri)))
            
        # Add metrics
        if pd.notna(row["population_density"]):
            g.add((country_uri, GM_ONT.hasPopulationDensity, Literal(row["population_density"], datatype=XSD.float)))
            
        if pd.notna(row["gdp_per_capita"]):
            g.add((country_uri, GM_ONT.hasGDPPerCapita, Literal(row["gdp_per_capita"], datatype=XSD.float)))
            
        if pd.notna(row["life_expectancy"]):
            g.add((country_uri, GM_ONT.hasLifeExpectancy, Literal(row["life_expectancy"], datatype=XSD.float)))
            
        if pd.notna(row["co2_emissions"]):
            g.add((country_uri, GM_ONT.hasCO2Emissions, Literal(row["co2_emissions"], datatype=XSD.float)))

    # Save VoID Metadata dynamically calculated
    g_void = Graph()
    VOID = Namespace("http://rdfs.org/ns/void#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    PROV = Namespace("http://www.w3.org/ns/prov#")
    
    g_void.bind("void", VOID)
    g_void.bind("dcterms", DCTERMS)
    g_void.bind("dcat", DCAT)
    g_void.bind("gmres", GM_RES)
    g_void.bind("foaf", FOAF)
    g_void.bind("prov", PROV)
    
    # 1. FOAF Agent (Creator)
    author_uri = GM_RES["agent/Mattia"]
    g_void.add((author_uri, RDF.type, FOAF.Person))
    g_void.add((author_uri, FOAF.name, Literal("Mattia", lang="it")))
    g_void.add((author_uri, FOAF.mbox, URIRef("mailto:mattia@university.edu")))
    
    # 2. PROV-O Activity (Pipeline Execution)
    activity_uri = GM_RES["activity/RunPipeline"]
    import datetime
    current_time = datetime.datetime.now().isoformat()
    current_date = datetime.date.today().isoformat()
    
    g_void.add((activity_uri, RDF.type, PROV.Activity))
    g_void.add((activity_uri, RDFS.label, Literal("RDF Generation Pipeline", lang="en")))
    g_void.add((activity_uri, PROV.startedAtTime, Literal(current_time, datatype=XSD.dateTime)))
    g_void.add((activity_uri, PROV.wasAssociatedWith, author_uri))
    
    # 3. DCAT Dataset
    dataset_uri = GM_RES["dataset/global_metrics_2020"]
    g_void.add((dataset_uri, RDF.type, VOID.Dataset))
    g_void.add((dataset_uri, RDF.type, DCAT.Dataset))
    g_void.add((dataset_uri, DCTERMS.title, Literal("Global Metrics 2020 Dataset", lang="en")))
    g_void.add((dataset_uri, DCTERMS.description, Literal("A 5-star Linked Open Data dataset containing global indicators from the World Bank for the year 2020.", lang="en")))
    g_void.add((dataset_uri, VOID.vocabulary, GM_ONT[""]))
    
    g_void.add((dataset_uri, DCTERMS.issued, Literal(current_date, datatype=XSD.date)))
    g_void.add((dataset_uri, DCTERMS.creator, author_uri))
    g_void.add((dataset_uri, OWL.versionInfo, Literal("1.0")))
    g_void.add((dataset_uri, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    g_void.add((dataset_uri, PROV.wasGeneratedBy, activity_uri))
    
    # 4. DCAT Distributions
    # A) RDF Distribution
    dist_rdf = GM_RES["distribution/rdf"]
    g_void.add((dataset_uri, DCAT.distribution, dist_rdf))
    g_void.add((dist_rdf, RDF.type, DCAT.Distribution))
    g_void.add((dist_rdf, DCAT.downloadURL, URIRef("file://processed/rdf/global_metrics.ttl")))
    g_void.add((dist_rdf, DCAT.mediaType, Literal("text/turtle")))
    g_void.add((dist_rdf, DCTERMS.format, Literal("TTL")))
    
    # B) CSV Distributions
    import os
    csv_dir = Path("processed/csv")
    if csv_dir.exists():
        for csv_file in csv_dir.glob("*.csv"):
            dist_csv = GM_RES[f"distribution/csv/{csv_file.stem}"]
            g_void.add((dataset_uri, DCAT.distribution, dist_csv))
            g_void.add((dist_csv, RDF.type, DCAT.Distribution))
            g_void.add((dist_csv, DCAT.downloadURL, URIRef(f"file://processed/csv/{csv_file.name}")))
            g_void.add((dist_csv, DCAT.mediaType, Literal("text/csv")))
            g_void.add((dist_csv, DCTERMS.format, Literal("CSV")))
    
    # Calculate statistics
    num_triples = len(g)
    num_entities = len(list(g.subjects(RDF.type, GM_ONT.Country)))
    g_void.add((dataset_uri, VOID.triples, Literal(num_triples, datatype=XSD.integer)))
    g_void.add((dataset_uri, VOID.entities, Literal(num_entities, datatype=XSD.integer)))
    
    void_path = "processed/rdf/void.ttl"
    g_void.serialize(destination=void_path, format="turtle")
    logger.info(f"VoID metadata saved to {void_path} with {num_triples} triples and {num_entities} entities.")

    rdf_path = "processed/rdf/global_metrics.ttl"
    g.serialize(destination=rdf_path, format="turtle")
    logger.info(f"Knowledge Graph saved to {rdf_path} (Format: Turtle)")
    
    logger.info("Running Local SPARQL Query...")
    # Local Query: Find all countries with GDP > 30000
    local_query = """
    PREFIX gmont: <http://globalmetrics.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    
    SELECT ?countryName ?gdp
    WHERE {
        ?country a gmont:Country ;
                 rdfs:label ?countryName ;
                 gmont:hasGDPPerCapita ?gdp .
        FILTER (?gdp > 30000)
    }
    ORDER BY DESC(?gdp)
    """
    
    results = g.query(local_query)
    logger.info("=== Countries with GDP > $30,000 ===")
    for row in results:
        logger.info(f"{row.countryName}: ${float(row.gdp):.2f}")
        
    logger.info("Running Federated SPARQL Query (DBpedia)...")
    # Note: SPARQLWrapper is used in actual Federated, but we can do a SERVICE query with rdflib if supported, 
    # or just use SPARQLWrapper directly.
    try:
        from SPARQLWrapper import SPARQLWrapper, JSON
        
        # We find a country in our dataset that is linked to DBpedia
        linked_countries = list(g.query("""
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            SELECT ?dbpediaUri WHERE {
                ?s owl:sameAs ?dbpediaUri .
            } LIMIT 5
        """))
        
        if linked_countries:
            dbp_uri = str(linked_countries[0].dbpediaUri)
            logger.info(f"Federated Querying DBpedia for info about: {dbp_uri}")
            
            sparql = SPARQLWrapper("http://dbpedia.org/sparql")
            sparql.setQuery(f"""
                PREFIX dbo: <http://dbpedia.org/ontology/>
                SELECT ?capitalName ?currencyName
                WHERE {{
                    <{dbp_uri}> dbo:capital ?capital .
                    ?capital rdfs:label ?capitalName .
                    FILTER (lang(?capitalName) = 'en')
                }} LIMIT 1
            """)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                logger.info(f"Capital of {dbp_uri}: {result['capitalName']['value']}")
                
    except Exception as e:
        logger.error(f"Federated query failed: {e}")

def create_datapackage():
    logger.info("Generating datapackage.json...")
    datapackage = {
        "name": "global-metrics-2020",
        "title": "Global Metrics 2020: GDP, Population Density, Life Expectancy and CO2 Emissions",
        "description": "Un dataset integrato a 5 stelle contenente indicatori globali della World Bank per l'anno 2020, interconnesso a DBpedia.",
        "licenses": [
            {
                "id": "CC-BY-4.0",
                "name": "Creative Commons Attribution 4.0",
                "url": "https://creativecommons.org/licenses/by/4.0/"
            }
        ],
        "resources": [
            {
                "name": "global_metrics_2020",
                "path": "processed/csv/global_metrics_2020.csv",
                "profile": "tabular-data-resource",
                "format": "csv",
                "encoding": "utf-8",
                "schema": {
                    "fields": [
                        {"name": "country_name", "type": "string", "description": "Name of the country"},
                        {"name": "country_code", "type": "string", "description": "ISO Alpha-3 code"},
                        {"name": "dbpedia_uri", "type": "string", "description": "DBpedia Resource URI (5-star link)"},
                        {"name": "population_density", "type": "number", "description": "Population density (people per sq. km)"},
                        {"name": "gdp_per_capita", "type": "number", "description": "GDP per capita (current US$)"},
                        {"name": "life_expectancy", "type": "number", "description": "Life expectancy at birth, total (years)"},
                        {"name": "co2_emissions", "type": "number", "description": "CO2 emissions (metric tons per capita)"}
                    ]
                }
            },
            {
                "name": "global_metrics_rdf",
                "path": "processed/rdf/global_metrics.ttl",
                "format": "ttl",
                "mediatype": "text/turtle",
                "description": "Knowledge Graph in formato Turtle (RDF) con ontologia fittizia e interlinking a DBpedia."
            }
        ]
    }
    
    with open("datapackage.json", "w", encoding="utf-8") as f:
        json.dump(datapackage, f, indent=4)
    logger.info("datapackage.json created successfully.")

if __name__ == "__main__":
    generate_rdf_and_queries()
    create_datapackage()
