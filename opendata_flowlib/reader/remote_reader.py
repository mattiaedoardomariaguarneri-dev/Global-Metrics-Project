import logging
from typing import Literal

import pandas as pd
import requests

from opendata_flowlib.reader.file_reader import read_csv, read_excel, read_json

logger = logging.getLogger("opendata_flowlib.reader.remote_reader")

def read_url(url: str, format: Literal["csv", "json", "excel"], **kwargs) -> pd.DataFrame:
    """Scarica e legge un file da un URL remoto in memoria, senza scriverlo su disco.

    Args:
        url: L'URL del file.
        format: Formato del file da decodificare ("csv", "json", "excel").
        **kwargs: Argomenti extra per i reader.

    Returns:
        DataFrame con i dati.
    """
    import io
    
    logger.info(f"Fetching data from URL: {url} as {format}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        if format == "csv":
            return pd.read_csv(io.StringIO(response.text), **kwargs)
        elif format == "json":
            return pd.read_json(io.StringIO(response.text), **kwargs)
        elif format == "excel":
            return pd.read_excel(io.BytesIO(response.content), **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")

    except Exception as e:
        logger.error(f"Error fetching/reading from URL {url}: {e}")
        raise ValueError(f"Impossibile leggere dall'URL specificato: {e}")

def read_ckan(endpoint: str, resource_id: str, **kwargs) -> pd.DataFrame:
    """Legge una risorsa da un portale CKAN (API datastore_search).

    Args:
        endpoint: URL base dell'API CKAN (es. https://dati.gov.it/api/3/action).
        resource_id: L'id della risorsa da estrarre.
        **kwargs: Parametri aggiuntivi per la chiamata API.

    Returns:
        DataFrame con i record estratti.
    """
    url = f"{endpoint.rstrip('/')}/datastore_search"
    params = {"resource_id": resource_id, "limit": 100000}
    params.update(kwargs)

    logger.info(f"Querying CKAN datastore: {url} for resource {resource_id}")
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if not data.get("success"):
            raise ValueError(f"CKAN API returned error: {data.get('error')}")

        records = data["result"]["records"]
        df = pd.DataFrame(records)
        logger.info(f"Successfully retrieved {len(df)} records from CKAN.")
        return df

    except Exception as e:
        logger.error(f"Error reading from CKAN {endpoint}: {e}")
        raise ValueError(f"Impossibile leggere da CKAN: {e}")

def read_sparql(endpoint: str, query: str, **kwargs) -> pd.DataFrame:
    """Esegue una query SPARQL e restituisce i risultati come DataFrame.

    Args:
        endpoint: L'URL dell'endpoint SPARQL.
        query: La query SPARQL da eseguire.
        **kwargs: Argomenti extra (ignorati).

    Returns:
        DataFrame con i risultati della query.
    """
    try:
        from SPARQLWrapper import SPARQLWrapper, JSON
    except ImportError:
        logger.error("SPARQLWrapper is required for read_sparql")
        raise ImportError("Install SPARQLWrapper (e.g. via pip install SPARQLWrapper)")

    logger.info(f"Executing SPARQL query on endpoint: {endpoint}")
    try:
        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        
        results = sparql.query().convert()
        bindings = results["results"]["bindings"]
        
        # Flatten dictionary
        parsed_data = []
        for row in bindings:
            parsed_row = {key: value["value"] for key, value in row.items()}
            parsed_data.append(parsed_row)
            
        df = pd.DataFrame(parsed_data)
        logger.info(f"Successfully retrieved {len(df)} rows from SPARQL endpoint.")
        return df

    except Exception as e:
        logger.error(f"Error executing SPARQL query: {e}")
        raise ValueError(f"Impossibile eseguire la query SPARQL: {e}")
