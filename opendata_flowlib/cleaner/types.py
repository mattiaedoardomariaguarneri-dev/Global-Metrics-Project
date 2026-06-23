import logging
from typing import List, Optional

import pandas as pd

logger = logging.getLogger("opendata_flowlib.cleaner.types")

def infer_and_cast_types(df: pd.DataFrame, strict: bool = False) -> pd.DataFrame:
    """Inferisce automaticamente e converte i tipi (date, numeri, booleani).

    Args:
        df: DataFrame da processare.
        strict: Se True, lancia eccezioni in caso di errore di conversione (ignorato qui, convert_dtypes è flessibile).

    Returns:
        DataFrame con i tipi castati inferiti.
    """
    logger.info("Inferring and casting types...")
    out_df = df.copy()
    for col in out_df.columns:
        if out_df[col].dtype == 'object' or out_df[col].dtype == 'string':
            # Try numeric
            try:
                num = pd.to_numeric(out_df[col], errors='ignore')
                if num.dtype != out_df[col].dtype:
                    out_df[col] = num
                    continue
            except:
                pass
            # Try datetime
            try:
                dt = pd.to_datetime(out_df[col], errors='ignore')
                if dt.dtype != out_df[col].dtype:
                    out_df[col] = dt
            except:
                pass
                
    out_df = out_df.convert_dtypes()
    return out_df

def cast_column(df: pd.DataFrame, column: str, dtype: str) -> pd.DataFrame:
    """Converte una singola colonna al tipo specificato.

    Args:
        df: DataFrame da processare.
        column: Nome della colonna.
        dtype: Tipo di destinazione (es. 'int64', 'float64', 'string').

    Returns:
        DataFrame con la colonna castata.
    """
    logger.info(f"Casting column {column} to {dtype}...")
    out_df = df.copy()
    if column in out_df.columns:
        out_df[column] = out_df[column].astype(dtype)
    else:
        logger.warning(f"Column {column} not found for casting.")
    return out_df

def parse_dates(df: pd.DataFrame, columns: List[str], format: Optional[str] = None) -> pd.DataFrame:
    """Converte colonne in formato datetime.

    Args:
        df: DataFrame da processare.
        columns: Lista di colonne da convertire.
        format: Formato data (es. '%Y-%m-%d').

    Returns:
        DataFrame con le colonne datetime.
    """
    logger.info(f"Parsing dates for columns {columns}...")
    out_df = df.copy()
    for col in columns:
        if col in out_df.columns:
            out_df[col] = pd.to_datetime(out_df[col], format=format, errors='coerce')
        else:
            logger.warning(f"Column {col} not found for date parsing.")
    return out_df
