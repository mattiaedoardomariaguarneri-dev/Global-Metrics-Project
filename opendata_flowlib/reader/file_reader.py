import logging
from pathlib import Path
from typing import Union

import pandas as pd

logger = logging.getLogger("opendata_flowlib.reader.file_reader")

def read_csv(path: Union[str, Path], encoding: str = "utf-8", separator: str = ",", **kwargs) -> pd.DataFrame:
    """Legge un file CSV e restituisce un DataFrame.

    Args:
        path: Percorso del file CSV.
        encoding: Encoding del file.
        separator: Separatore di colonne.
        **kwargs: Argomenti aggiuntivi passati a pd.read_csv.

    Returns:
        DataFrame con i dati del file.

    Raises:
        FileNotFoundError: Se il file non esiste.
        ValueError: Se il file non è leggibile.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File non trovato: {path}")

    try:
        df = pd.read_csv(path_obj, encoding=encoding, sep=separator, **kwargs)
        logger.info(f"Successfully read CSV from {path}. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error reading CSV {path}: {e}")
        raise ValueError(f"Impossibile leggere il file CSV: {e}")

def read_excel(path: Union[str, Path], sheet_name: Union[str, int] = 0, **kwargs) -> pd.DataFrame:
    """Legge un file Excel (.xlsx) e restituisce un DataFrame.

    Args:
        path: Percorso del file Excel.
        sheet_name: Nome o indice del foglio da leggere.
        **kwargs: Argomenti aggiuntivi passati a pd.read_excel.

    Returns:
        DataFrame con i dati del foglio Excel.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File non trovato: {path}")

    try:
        df = pd.read_excel(path_obj, sheet_name=sheet_name, **kwargs)
        logger.info(f"Successfully read Excel from {path}. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error reading Excel {path}: {e}")
        raise ValueError(f"Impossibile leggere il file Excel: {e}")

def read_json(path: Union[str, Path], orient: str = "records", **kwargs) -> pd.DataFrame:
    """Legge un file JSON e restituisce un DataFrame.

    Args:
        path: Percorso del file JSON.
        orient: Formato JSON atteso.
        **kwargs: Argomenti aggiuntivi passati a pd.read_json.

    Returns:
        DataFrame con i dati del file JSON.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File non trovato: {path}")

    try:
        df = pd.read_json(path_obj, orient=orient, **kwargs)
        logger.info(f"Successfully read JSON from {path}. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error reading JSON {path}: {e}")
        raise ValueError(f"Impossibile leggere il file JSON: {e}")

def read_parquet(path: Union[str, Path], **kwargs) -> pd.DataFrame:
    """Legge un file Parquet e restituisce un DataFrame.

    Args:
        path: Percorso del file Parquet.
        **kwargs: Argomenti aggiuntivi passati a pd.read_parquet.

    Returns:
        DataFrame con i dati del file Parquet.
    """
    path_obj = Path(path)
    if not path_obj.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File non trovato: {path}")

    try:
        df = pd.read_parquet(path_obj, **kwargs)
        logger.info(f"Successfully read Parquet from {path}. Shape: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error reading Parquet {path}: {e}")
        raise ValueError(f"Impossibile leggere il file Parquet: {e}")

def read_pdf(path: Union[str, Path], page: Union[int, list[int], None] = None, **kwargs) -> pd.DataFrame:
    """Estrae tabelle da un file PDF usando pdfplumber.

    Se page=None, restituisce la prima tabella trovata in assoluto.
    Altrimenti estrae dalle pagine specificate (1-indexed).

    Args:
        path: Percorso del file PDF.
        page: Numero di pagina o lista di pagine da cui estrarre. None per la prima trovata.
        **kwargs: Argomenti extra per l'estrazione.

    Returns:
        DataFrame con i dati estratti (le tabelle vengono concatenate).
    """
    import pdfplumber

    path_obj = Path(path)
    if not path_obj.exists():
        logger.error(f"File not found: {path}")
        raise FileNotFoundError(f"File non trovato: {path}")

    dfs = []
    try:
        with pdfplumber.open(path_obj) as pdf:
            pages_to_process = []
            if page is None:
                pages_to_process = range(len(pdf.pages))
            elif isinstance(page, int):
                pages_to_process = [page - 1] # 0-indexed in pdfplumber
            else:
                pages_to_process = [p - 1 for p in page]

            for i in pages_to_process:
                if 0 <= i < len(pdf.pages):
                    p = pdf.pages[i]
                    tables = p.extract_tables()
                    for table in tables:
                        if table:
                            df_table = pd.DataFrame(table[1:], columns=table[0])
                            dfs.append(df_table)
                            if page is None:
                                break
                if page is None and dfs:
                    break
        
        if not dfs:
            logger.warning(f"No tables found in PDF {path}")
            return pd.DataFrame()

        result_df = pd.concat(dfs, ignore_index=True)
        logger.info(f"Successfully read tables from PDF {path}. Final shape: {result_df.shape}")
        return result_df

    except Exception as e:
        logger.error(f"Error reading PDF {path}: {e}")
        raise ValueError(f"Impossibile estrarre tabelle dal PDF: {e}")
