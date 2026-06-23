# Ontologia, Integrazione Protégé e Query SPARQL

## 🧠 Il Meccanismo dell'Ontologia
La logica della T-Box (salvata in `ontology.ttl` e fusa in `global_metrics.ttl`) è progettata per il perfetto tracciamento della semantica:
- **Classi Rigorose**: Uso esplicito di `owl:Class` (es. `gmont:Country`).
- **Data Properties Uniformi**: Tutte le metriche numeriche del dataset sono mappate come `owl:DatatypeProperty`, imponendo in modo restrittivo il loro *domain* (`gmont:Country`) e il loro *range* (`xsd:float`). Sono documentate storicamente con `dcterms:date` e tracciate alla sorgente (World Bank) tramite `prov:wasDerivedFrom`. L'unità di misura è dichiarata formalmente con `qudt:unit`.
- **Ancoraggio SKOS**: Grazie a `skos:prefLabel`, `skos:notation`, e `skos:scopeNote`, l'ontologia espone in modo umano le regole formali per interpretare le metriche. 
- **Object Properties**: I link enciclopedici avvengono tramite `gmont:exactMatchDBpedia`, a sua volta definita come *subProperty* di `owl:sameAs`.

### Integrazione in Protégé
Sia che si apra in **Protégé**, in GraphDB o in tool web come RDFShape, il caricamento di `global_metrics.ttl` previene qualunque tipo di "smarrimento delle entità". Fondere lo schema direttamente assieme alle istanze dell'A-Box assicura al visualizzatore di percepire simultaneamente la logica strutturale e le 187 istanze (gli individui reali dei Paesi) nella lista delle `Individuals`, senza doverle incrociare o dedurre manualmente da due file differenti.

---

## 🔎 Query SPARQL Esemplificative
L'approccio "merge and rule" permette di attraversare contemporaneamente i parametri macroeconomici, ambientali e sanitari. 

### 1. Gli "Heavy Emitters"
Trova i paesi con alto GDP (> 40.000$) e un'altissima densità di popolazione (> 200), ordinandoli per la quantità di CO2 prodotta.
```sparql
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
```

### 2. I Paesi "Paradiso"
Mostra la reale utilità del Knowledge Graph unificato: cercare paesi floridi (GDP > 30.000$) che tuttavia riescono a mantenere le emissioni di CO2 incredibilmente basse (< 5 tonnellate). 
```sparql
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
```

### 3. Il Dividendo della Longevità
Analizza l'aspettativa di vita specificamente tra l'élite globale dei redditi (> 50.000$).
```sparql
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
```

### 4. Federated Querying: Oltre il Grafo Locale
Grazie alla nostra Open Data 5★ connection: peschiamo dal nostro grafo solo i Paesi super-longevi (> 82 anni), poi in tempo reale lanciamo una query SPARQL *federata* al server di DBpedia per estrapolare la capitale di quel paese specifico.
```sparql
PREFIX gmont: <http://globalmetrics.org/ontology/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dbo: <http://dbpedia.org/ontology/>

SELECT ?countryName ?lifeExpectancy ?capitalName
WHERE {
    ?country a gmont:Country ;
             rdfs:label ?countryName ;
             gmont:hasLifeExpectancy ?lifeExpectancy ;
             gmont:exactMatchDBpedia ?dbpediaURI .
             
    FILTER (?lifeExpectancy > 82)
    
    SERVICE <http://dbpedia.org/sparql> {
        ?dbpediaURI dbo:capital ?capitalURI .
        ?capitalURI rdfs:label ?capitalName .
        FILTER (lang(?capitalName) = 'en')
    }
}
ORDER BY DESC(?lifeExpectancy)
```
