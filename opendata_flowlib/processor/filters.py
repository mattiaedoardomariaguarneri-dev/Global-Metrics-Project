import logging
from typing import List

import pandas as pd

logger = logging.getLogger("opendata_flowlib.processor.filters")

def filter_rows(df: pd.DataFrame, condition: str) -> pd.DataFrame:
    """Filtra righe usando una stringa di query pandas.

    Args:
        df: DataFrame da processare.
        condition: Stringa di query per pd.DataFrame.query().

    Returns:
        DataFrame filtrato.
    """
    logger.info(f"Filtering rows with condition: {condition}")
    return df.query(condition)

def select_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Seleziona solo le colonne specificate.

    Args:
        df: DataFrame da processare.
        columns: Lista di colonne da mantenere.

    Returns:
        DataFrame con solo le colonne selezionate.
    """
    logger.info(f"Selecting columns: {columns}")
    return df[columns].copy()

def drop_columns(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """Rimuove le colonne specificate.

    Args:
        df: DataFrame da processare.
        columns: Lista di colonne da rimuovere.

    Returns:
        DataFrame senza le colonne specificate.
    """
    logger.info(f"Dropping columns: {columns}")
    return df.drop(columns=columns)
