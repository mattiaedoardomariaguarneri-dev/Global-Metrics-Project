=========================================================
DIZIONARIO DEI METADATI - KNOWLEDGE GRAPH (RDF/TTL)
=========================================================

Questo file descrive la struttura semantica, l'ontologia e i metadati dei file Turtle (.ttl) contenuti nella cartella `processed/rdf/`.

ELENCO DEI FILE:
1. global_metrics.ttl : Knowledge Graph completo (A-Box + T-Box). Contiene sia le istanze dei paesi che lo schema ontologico integrato.
2. ontology.ttl       : Schema puro (solo T-Box). Utile per l'importazione nei tool di modellazione (es. Protégé).
3. void.ttl           : Metadati descrittivi del dataset macroscopico basati sui vocabolari VoID e DCAT.
4. catalog-v001.xml   : File di servizio autogenerato per la gestione locale dell'ontologia.

=========================================================
VOCABOLARI CONTROLLATI E PREFISSI UTILIZZATI
=========================================================
- gmont:   <http://globalmetrics.org/ontology/> (Ontologia Proprietaria del Progetto)
- skos:    <http://www.w3.org/2004/02/skos/core#> (Annotazioni, labels e definizioni standard)
- rdfs:    <http://www.w3.org/2000/01/rdf-schema#> (Schema RDF di base)
- owl:     <http://www.w3.org/2002/07/owl#> (Classi, DatatypeProperty, ObjectProperty)
- xsd:     <http://www.w3.org/2001/XMLSchema#> (Tipi di dato formali)
- dcterms: <http://purl.org/dc/terms/> (Descrizioni e attribuzioni documentali)
- void:    <http://rdfs.org/ns/void#> (Descrittore formale del dataset e dei suoi vocabolari)
- dcat:    <http://www.w3.org/ns/dcat#> (Catalogo unificato dei dati e delle distribuzioni)
- foaf:    <http://xmlns.com/foaf/0.1/> (Identità dell'Agente/Creatore)
- prov:    <http://www.w3.org/ns/prov#> (Tracciabilità temporale e derivazione delle fonti)
- qudt:    <http://qudt.org/schema/qudt/> (Dichiarazione rigorosa delle unità di misura)

=========================================================
STRUTTURA DELL'ONTOLOGIA (SCHEMA E METADATI DCAT)
=========================================================

CLASSI E ATTIVITA' (owl:Class, foaf:Person, prov:Activity)
---------------------------------------------------------
- gmont:Country
  Descrizione: Un corpo territoriale distinto o entità politica sovrana.
- gmres:agent/Mattia (foaf:Person)
  Descrizione: Il creatore istituzionale responsabile della curatela del dataset.
- gmres:activity/RunPipeline (prov:Activity)
  Descrizione: L'esecuzione computazionale che ha scaturito il dataset RDF in tempo reale.


PROPRIETA' DI COLLEGAMENTO (owl:ObjectProperty)
---------------------------------------------------------
- gmont:exactMatchDBpedia (subPropertyOf owl:sameAs)
  Descrizione: Collega formalmente la classe gmont:Country all'URI della medesima nazione su DBpedia per l'interoperabilità LOD 5★.


PROPRIETA' DEI DATI (owl:DatatypeProperty)
---------------------------------------------------------
Tutte le proprietà seguenti hanno come Dominio (rdfs:domain) la classe `gmont:Country` e come Codominio (rdfs:range) il tipo di dato `xsd:float`.
Sono storicamente ancorate tramite `dcterms:date` all'anno 2020. Tutte espongono un link URI ufficiale alla Banca Mondiale tramite `prov:wasDerivedFrom`.

1. gmont:hasPopulationDensity
   - skos:prefLabel: Population Density
   - skos:notation: POP_DENS
   - skos:scopeNote: Calcolata come popolazione totale divisa per area territoriale (persone/kmq).
   - qudt:unit: People per sq. km

2. gmont:hasGDPPerCapita
   - skos:prefLabel: GDP per capita (US$)
   - skos:notation: GDP_PC
   - skos:scopeNote: Prodotto Interno Lordo diviso per la popolazione di metà anno (in US$ correnti).
   - qudt:unit: Current US$

3. gmont:hasLifeExpectancy
   - skos:prefLabel: Life Expectancy at Birth
   - skos:notation: LIFE_EXP
   - skos:scopeNote: Anni stimati di vita media alla nascita, mantenendo gli attuali tassi di mortalità.
   - qudt:unit: Years

4. gmont:hasCO2Emissions
   - skos:prefLabel: CO2 Emissions per capita
   - skos:notation: CO2_PC
   - skos:scopeNote: Emissioni derivanti dalla combustione di combustibili fossili (tonnellate pro capite).
   - qudt:unit: Metric tons per capita
