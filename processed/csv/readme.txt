=========================================================
DIZIONARIO DEI METADATI - DATASET TABELLARI (CSV)
=========================================================

Questo file descrive i metadati e la struttura dei file CSV contenuti nella cartella `processed/csv/`.

ELENCO DEI FILE:
1. global_metrics_2020.csv : Dataset unificato contenente tutte le metriche per l'anno 2020.
2. global_metrics_with_index_2020.csv : Variante del dataset unificato.
3. co2_2020.csv : Dataset isolato relativo alle emissioni di CO2.
4. gdp_2020.csv : Dataset isolato relativo al GDP pro capite.
5. life_exp_2020.csv : Dataset isolato relativo all'aspettativa di vita.
6. pop_density_2020.csv : Dataset isolato relativo alla densità di popolazione.

NOTA METADATI DCAT: Tutti i file CSV qui elencati sono formalmente esposti come `dcat:Distribution` (con MimeType `text/csv`) all'interno del catalogo semantico principale (`processed/rdf/void.ttl`).

=========================================================
STRUTTURA DELLE COLONNE (SCHEMA DEI DATI)
=========================================================

1. country_name
   - Formato: Stringa (Testo)
   - Descrizione: Nome canonico in lingua inglese della nazione/Stato sovrano (normalizzato).

2. country_code
   - Formato: Stringa (3 caratteri)
   - Descrizione: Codice ISO 3166-1 alpha-3 identificativo della nazione.

3. population_density
   - Formato: Numero decimale (Float)
   - Unità di misura: Persone per chilometro quadrato di superficie terrestre.
   - Descrizione: Densità di popolazione.

4. gdp_per_capita
   - Formato: Numero decimale (Float)
   - Unità di misura: Dollari Statunitensi (US$) correnti.
   - Descrizione: Prodotto Interno Lordo (Gross Domestic Product) pro capite.

5. life_expectancy
   - Formato: Numero decimale (Float)
   - Unità di misura: Anni.
   - Descrizione: Aspettativa di vita alla nascita.

6. co2_emissions
   - Formato: Numero decimale (Float)
   - Unità di misura: Tonnellate metriche pro capite.
   - Descrizione: Emissioni di anidride carbonica (CO2).

7. dbpedia_uri
   - Formato: URI (Stringa)
   - Descrizione: Identificatore Univoco di Risorsa del paese su DBpedia (Linked Open Data 5-star interlinking). Sempre posizionato come ultima colonna.
