import logging
from typing import List, Literal, Optional

import pandas as pd

logger = logging.getLogger("opendata_flowlib.cleaner.dedup")

def drop_duplicates(
    df: pd.DataFrame,
    subset: Optional[List[str]] = None,
    keep: Literal["first", "last"] = "first"
) -> pd.DataFrame:
    """Rimuove righe duplicate.

    Args:
        df: DataFrame da processare.
        subset: Lista di colonne su cui cercare i duplicati. Se None, usa tutte le colonne.
        keep: Quale duplicato mantenere ('first' o 'last').

    Returns:
        DataFrame senza duplicati.
    """
    logger.info(f"Dropping duplicates (subset={subset}, keep={keep})...")
    out_df = df.drop_duplicates(subset=subset, keep=keep)
    logger.info(f"Dropped {len(df) - len(out_df)} duplicate rows.")
    return out_df

def flag_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
    """Aggiunge colonna '_is_duplicate' booleana.

    Args:
        df: DataFrame da processare.
        subset: Lista di colonne su cui testare i duplicati. Se None, tutte le colonne.

    Returns:
        DataFrame con la nuova colonna '_is_duplicate'.
    """
    logger.info(f"Flagging duplicates (subset={subset})...")
    out_df = df.copy()
    out_df['_is_duplicate'] = out_df.duplicated(subset=subset, keep=False)
    return out_df
