# Verifica di Conformità: Data.europa.eu Data Quality Guidelines

Il progetto "Global Metrics" è stato valutato rispetto alle linee guida ufficiali europee sulla qualità dei dati aperti. Di seguito viene riportata la mappatura tra le raccomandazioni del documento e le implementazioni tecniche della nostra pipeline.

## 1. Findability (Rintracciabilità)
- **Describe your data with metadata**: Il progetto genera un `datapackage.json` (struttura standardizzata) che descrive esaustivamente ogni colonna dei CSV generati, la codifica e i tipi di dato, facilitandone l'indicizzazione.
- **Mark null values explicitly**: Sebbene lo standard CSV spesso presenti campi vuoti per i null, la libreria `opendata_flowlib` mette a disposizione il modulo `nulls.py` (es. `fill_nulls`) per esplicitare i valori mancanti (es. riempiendoli con `NaN`, `NULL` o un valore di default) ed eliminare le righe prive di informazione (`drop_null_rows`).

## 2. Accessibility (Accessibilità)
- **Publish data without restrictions**: I formati prodotti (`.csv`, `.ttl`, `.json`) sono completamente aperti e non proprietari, garantendo accessibilità senza barriere (no password o formati binari chiusi).

## 3. Interoperability (Interoperabilità)
### Raccomandazioni Generali
- **Formatting of decimal numbers and thousands**: Questo è uno dei punti di forza del progetto. La funzione `normalize_numeric_values` del modulo `cleaner/numbers.py` è stata progettata esattamente per questo: sostituisce la virgola decimale con il punto e rimuove i separatori delle migliaia, producendo numeri puri processabili (es. `1.234,56` diventa `1234.56`).
- **Standardised character encoding**: Sia in lettura (`read_csv`) che in scrittura (`save_csv`) e nel pacchetto JSON, viene imposto di default l'encoding `UTF-8`.

### Raccomandazioni specifiche per il formato CSV
- **Use a semicolon as a delimiter**: La funzione `save_csv` accetta il parametro `separator` che permette agilmente di passare dalla virgola (default internazionale) al punto e virgola (scelta raccomandata a livello europeo per evitare conflitti con i decimali).
- **Use one file per table**: I dati in output sono consolidati in una singola tabella piana denormalizzata (`global_metrics_2020.csv`), rispettando appieno questa regola.
- **Avoid white space and additional information in the file**: I dataset grezzi della World Bank includevano 4 righe iniziali di metadati descrittivi (es. "Last Updated Date"). Il nostro orchestratore `Pipeline` salta selettivamente tali righe (`skiprows=4`) in fase di ingestione per esportare solo dati tabellari puri, senza testo estraneo che bloccherebbe il parsing automatico.
- **Insert column headers**: Attraverso la funzione `normalize_headers(case="snake")`, tutte le intestazioni originali (spesso contenenti spazi, parentesi o caratteri speciali) vengono ripulite e unificate in un formato standard `snake_case` (es. `GDP per Capita` diventa `gdp_per_capita`), essenziale per l'interoperabilità e la leggibilità semantica.
- **Ensure that all rows have the same number of columns**: Il salvataggio finale avviene mediante le strutture dati coerenti di Pandas, che previene l'aggiunta accidentale di colonne o righe disallineate.

### Raccomandazioni specifiche per il formato RDF
- **Use HTTP URIs to denote resources**: Tutte le entità del dominio (i Paesi) e i predicati sono stati mappati come URIs HTTP valide (`http://globalmetrics.org/resource/...` e `http://globalmetrics.org/ontology/...`).
- **Use namespaces when possible**: Nello script `generate_rdf.py`, sono stati registrati i namespace `gmont`, `gmres`, `dbpedia` usando l'oggetto `Namespace` di `rdflib`, rendendo il file `.ttl` più compatto e leggibile.
- **Use existing vocabularies when possible**: Per le operazioni di data augmentation è stato usato il namespace e vocabolario ufficiale di **DBpedia**. La proprietà custom `gmont:exactMatchDBpedia` è dichiarata come sottoproprietà di `owl:sameAs`, in modo da mantenere il legame semantico corretto tra entità locali e risorse remote.

## 4. Reusability (Riutilizzabilità)
- **Remove duplicates**: La libreria garantisce l'unicità dei record fornendo la funzione `drop_duplicates` per la bonifica automatica in fase di data prep.

## 5. Improving the Openness Level (Modello a 5 Stelle)
Il progetto rispetta progressivamente tutti i requisiti del Modello a 5 stelle di Tim Berners-Lee:
- **★**: Licenza aperta (espressa in `datapackage.json` come CC-BY-4.0).
- **★★**: Dati strutturati machine-readable (CSV via Pandas).
- **★★★**: Utilizzo di formati aperti non proprietari (CSV, JSON invece di XLS).
- **★★★★**: Utilizzo di URI aperte per denotare risorse e vocabolari RDF (file `global_metrics.ttl`).
- **★★★★★**: Interlinking con base dati esterna. Il dataset unisce i propri concetti locali a quelli di **DBpedia** e consente di effettuare federated query via SPARQL.
