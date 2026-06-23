# Architettura del Progetto

## ⚙️ La Pipeline Dati
Il progetto non si limita a raccogliere e presentare dati statici, ma offre una **data pipeline (in Python) completamente automatizzata**, riproducibile, e altamente modulare. Il codice si sviluppa tramite approcci *Fluent Interface* per la pulizia dei CSV nativi.

### Racconto del Workflow (Storytelling)

Il flusso di lavoro segue un percorso logico lineare:

1. **Inception e Raccolta Dati**: Il processo inizia nella cartella `SOURCES`, che contiene i CSV grezzi della World Bank. Data la presenza di metadati intrusivi nelle prime 4 righe di questi file, il nostro `file_reader` è stato configurato per saltare l'header sporco.
2. **Pulizia e Normalizzazione**: I dati grezzi vengono presi in carico dal modulo `cleaner`. Le intestazioni vengono normalizzate in formato *snake_case* per evitare problemi di encoding e spaziature. Le colonne non necessarie vengono scartate.
3. **Selezione e Trasformazione**: Il `processor` isola la colonna dell'anno di interesse (2020) e la rinomina con il nome dell'indicatore specifico (es. `population_density`). Vengono anche rimossi i record privi di dati per quell'anno.
4. **Arricchimento Semantico**: Il dataframe passa attraverso l'`enrich_with_country_id`. Usando un file di lookup (`countries_lookup.csv`), i nomi testuali dei paesi vengono confrontati (ignorando il case) e tradotti in URI di DBpedia.
5. **Merging**: I 4 dataset, ora puliti e arricchiti, vengono uniti (merge) in un unico grande dataset: `global_metrics_2020.csv`.
6. **Costruzione del Grafo e SPARQL**: Lo script finale `generate_rdf.py` prende il dataset unificato e, riga per riga, costruisce le triple RDF usando `rdflib`. Vengono poi eseguite due query di validazione:
   - *Locale*: Filtra le nazioni nel nostro file `.ttl` con un PIL superiore a 30.000$.
   - *Federata*: Prende un'URI dal nostro grafo (es. Afghanistan), contatta l'endpoint remoto di DBpedia e ne estrae la capitale, dimostrando la potenza dei Linked Open Data.
7. **Packaging**: Il processo termina con la generazione di un `datapackage.json` formale, rendendo l'intero pacchetto condivisibile e pronto per l'ingestion da parte di cataloghi open data (es. CKAN).

### 1. Ingestion & Cleaning
I file CSV grezzi forniti dalla World Bank contengono fino a 70 colonne in eccesso per gli anni storici.
- **Normalizzazione Header e Drop**: Un processo automatizzato scarta tutte le misurazioni pre-2020 e rinomina automaticamente la colonna anno dell'indicatore.
- **Filtraggio Aggregati**: I dataset originali comprendono aree geografiche composite (es. "Sub-Saharan Africa", "High income"). Un dizionario custom viene utilizzato per estirpare queste macro-regioni dal dataset, garantendo l'isolamento esclusivo degli stati sovrani.

### 2. Entity Resolution & Lookups
Per unire perfettamente 4 file asimmetrici, il sistema usa il lookup `source/countries_lookup.csv` (inizializzato dallo script `bootstrap_lookup.py`).
- **Risoluzione Nomi**: Converte discrepanze (es. "Korea, Rep." e "South Korea") nel nome canonico univoco associato al loro codice ISO Alpha-3.
- **Bootstrap Interlinking**: Fin dalla costruzione del CSV intermedio, la pipeline esegue il lookup asincrono contro Wikipedia/DBpedia in modo da stoccare fin da subito l'URI utile per il formato LOD 5★.

### 3. Generazione Semantica (CSV to RDF)
Superata la fase di Data Science classica (che archivia i dataset tabellari in `processed/csv/`), entra in funzione il bridge semantico orchestrato in `generate_rdf.py`:
- Invece di disseminare indicatori sparsi, la pipeline condensa tutto nel super-file `processed/rdf/global_metrics.ttl` (che mescola T-Box schematica e A-Box istanziata).
- Lo schema puro (senza istanze) viene esportato separatamente in `ontology.ttl` per uso modellistico.
- Genera infine i metadati DCAT/VoID e l'equivalente tabular-resource standard JSON (`datapackage.json`).

### 3.3 Organizzazione del progetto

L'intero repository è stato organizzato in modo da separare chiaramente le diverse responsabilità della pipeline, distinguendo tra codice sorgente, dati di input, artefatti elaborati e documentazione tecnica.

Le principali directory possono essere così sintetizzate:

- **opendata_flowlib/** contiene la libreria Python che implementa i moduli di lettura, pulizia, trasformazione, arricchimento e serializzazione dei dati;
- **scripts/** raccoglie gli script che orchestrano le varie fasi del progetto, come la preparazione dei dataset, la generazione dei grafici e la creazione del grafo RDF;
- **raw_data/** ospita i file CSV originali provenienti dalla World Bank, conservandone la struttura iniziale e i metadati di origine;
- **processed/** contiene gli output della pipeline, tra cui i dataset puliti, i CSV unificati, i file RDF e i report derivati;
- **lookup_data/** conserva i file di mapping utilizzati per l'enrichment semantico e per la risoluzione delle entità;
- **charts/** raccoglie le visualizzazioni e le mappe generate per l'analisi comparativa;
- **docs/** include la documentazione tecnica utile a comprendere architettura, ontologia e workflow del progetto.

Questa organizzazione consente di distinguere chiaramente il software riutilizzabile dagli artefatti prodotti durante l'elaborazione, migliorando la leggibilità complessiva del repository.

L'utilizzo di una struttura ordinata facilita inoltre la manutenzione del progetto e rende immediatamente individuabili le diverse componenti dell'applicazione.

## 💻 Esempi di Funzionamento (opendata_flowlib)
La libreria `opendata_flowlib` fa della *Fluent Interface* il suo punto di forza. Tutte le manipolazioni vengono accodate su un oggetto `Pipeline` che garantisce leggibilità e manutenibilità estrema.

### Esempio 1: La catena di pulizia principale
Ecco un estratto reale di come i file World Bank (complessi e sporchi) vengono digeriti dal sistema in una semplice sequenza di step concatenati:

```python
from opendata_flowlib.pipeline import Pipeline
from opendata_flowlib.reader import read_csv
from opendata_flowlib.cleaner import drop_unnamed_columns, normalize_headers
from opendata_flowlib.processor import select_columns, filter_rows

result = (
    Pipeline(file_path)
    .process(read_csv)
    .process(drop_unnamed_columns)
    .process(normalize_headers)
    .process(select_columns, columns=["country_name", "country_code", "2020"])
    .process(filter_rows, condition="`2020`.notna()")
)
df_pulito = result.df
```

### Esempio 2: L'Arricchimento tramite Lookup e Entity Resolution
Una volta che i dati base sono stati isolati, la pipeline applica i moduli di *enrichment*. L'interlinking a DBpedia e il filtraggio delle macro-regioni (come "World" o "High income") avvengono in modo reattivo:

```python
from opendata_flowlib.enricher import enrich_with_country_id

# ... accodato alla pipeline precedente ...
    .process(enrich_with_country_id, lookup_path="source/countries_lookup.csv")
    .process(filter_rows, condition="dbpedia_uri.notna()") # Scarta aggregati senza URI
    .process(normalize_country_name, lookup_path="source/countries_lookup.csv")
```

La funzione core `normalize_country_name` è un chiaro esempio di risoluzione delle entità:
```python
def normalize_country_name(df: pd.DataFrame, lookup_path: str) -> pd.DataFrame:
    """Sostituisce il nome divergente del dataset col nome canonico ufficiale."""
    lookup = pd.read_csv(lookup_path)
    mapping = dict(zip(lookup["country_code"], lookup["country_name"]))
    df["country_name"] = df["country_code"].map(mapping).fillna(df["country_name"])
    return df
```
### Analisi approfondita della Pipeline della libreria

---

## 1. Overview & Principi Architetturali
**Obiettivo:** Libreria Python modulare per la costruzione di pipeline di analisi dati, orientata alla pulizia, arricchimento e normalizzazione di dataset eterogenei per il raggiungimento delle 5 stelle open data.

**Principi:**
- Ogni funzione di trasformazione applica modifiche ad un DataFrame pandas restituendone una copia (nessun side effect in-place dove possibile).
- La firma uniforme delle funzioni di step è `(df: pd.DataFrame, **kwargs) -> pd.DataFrame`.
- Il meccanismo di concatenazione (Pipeline) è completamente disaccoppiato dalle singole funzioni logiche.
- Integrazione nativa con logger per tenere traccia delle esecuzioni (righe scartate, shape, tempi di esecuzione).
- Compatibilità totale con `pandas >= 2.0` e tipizzazione forte (`typing`).

## 2. Specifiche Modulo `reader`

### `file_reader.py`
```python
def read_csv(path: str | Path, encoding: str = "utf-8", separator: str = ",", **kwargs) -> pd.DataFrame
def read_excel(path: str | Path, sheet_name: str | int = 0, **kwargs) -> pd.DataFrame
def read_json(path: str | Path, orient: str = "records", **kwargs) -> pd.DataFrame
def read_parquet(path: str | Path, **kwargs) -> pd.DataFrame
def read_pdf(path: str | Path, page: int | list[int] | None = None, **kwargs) -> pd.DataFrame
```

**Comportamento atteso:**
- Le funzioni caricano i dati da disco.
- Viene garantito il sollevamento di errori esplicativi in caso di file non trovato (`FileNotFoundError`) o corrotto (`ValueError`).
- La funzione per PDF fa uso di `pdfplumber` per estrarre le tabelle.

### `remote_reader.py`
```python
def read_url(url: str, format: Literal["csv", "json", "excel"], **kwargs) -> pd.DataFrame
def read_ckan(endpoint: str, resource_id: str, **kwargs) -> pd.DataFrame
def read_sparql(endpoint: str, query: str, **kwargs) -> pd.DataFrame
```

---

## 3. Specifiche Modulo `cleaner`

Tutte le funzioni hanno firma principale: `(df: pd.DataFrame, **kwargs) -> pd.DataFrame`

### `headers.py`
```python
def normalize_headers(df: pd.DataFrame, case: Literal["snake", "lower", "upper"] = "snake") -> pd.DataFrame
def rename_columns(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame
def drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame
```

### `numbers.py` & `types.py`
```python
def strip_column_suffixes(df, suffixes: Iterable[str] = ("_ton",), percent_suffix: str = "_pct") -> pd.DataFrame
def normalize_numeric_values(df, columns: list[str] | None = None, thousand_separators: Iterable[str] = (".", " "), infer_numeric: bool = False, strip_percent: bool = True) -> pd.DataFrame
def infer_and_cast_types(df: pd.DataFrame, strict: bool = False) -> pd.DataFrame
```

### `nulls.py` & `dedup.py`
```python
def drop_null_rows(df: pd.DataFrame, threshold: float = 1.0) -> pd.DataFrame
def flag_nulls(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame
def drop_duplicates(df: pd.DataFrame, subset: list[str] | None = None, keep: Literal["first", "last"] = "first") -> pd.DataFrame
```

---

## 4. Specifiche Modulo `processor` e `enricher`

### `filters.py`
```python
def filter_rows(df: pd.DataFrame, condition: str) -> pd.DataFrame
def select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame
```

### `enricher.py`
```python
def enrich_with_country_id(
    df: pd.DataFrame,
    country_lookup_path: str | Path,
    source_column: str,
    output_column: str = "iso_alpha3",
    country_label_column: str = "country_name",
    country_code_column: str = "iso_alpha3",
    separator: str = ",",
    encoding: str = "utf-8",
    log_path: str | Path | None = None
) -> pd.DataFrame
```
- Esegue un match *case-insensitive* per estrarre codici univoci (es. ISO o DBpedia URIs).

---

## 5. Specifiche Modulo `pipeline`

Il modulo espone la classe `Pipeline` che memorizza una coda di operazioni da eseguire in sequenza.

### Classe `Pipeline`
```python
class Pipeline:
    def __init__(self, on_error: Literal["raise", "skip", "warn"] = "raise"): ...
    def read(self, reader_fn: Callable, *args, **kwargs) -> "Pipeline": ...
    def clean(self, cleaner_fn: Callable, **kwargs) -> "Pipeline": ...
    def process(self, processor_fn: Callable, **kwargs) -> "Pipeline": ...
    def run(self) -> PipelineResult: ...
```

### Struttura `PipelineResult`
```python
@dataclass
class PipelineResult:
    df: pd.DataFrame            # Risultato finale
    figures: list[Any]          # Eventuali grafici generati
    steps_log: list[StepLog]    # Statistiche su tempo di esecuzione e dim dei dati
    errors: list[Exception]     # Errori ignorati se on_error="skip"
```

L'invocazione di `run()` itera su tutti gli step, esegue le funzioni passate dinamicamente registrando la durata in millisecondi (ms) e il differenziale tra numero di righe e colonne d'ingresso rispetto a quelle in uscita.