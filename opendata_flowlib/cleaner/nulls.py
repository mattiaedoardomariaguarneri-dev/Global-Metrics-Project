import logging
from typing import List, Literal, Optional

import pandas as pd

logger = logging.getLogger("opendata_flowlib.cleaner.nulls")

def drop_null_rows(df: pd.DataFrame, threshold: float = 1.0) -> pd.DataFrame:
    """Rimuove righe con proporzione di null superiore a threshold.

    threshold=1.0 -> rimuove solo righe completamente null
    threshold=0.5 -> rimuove righe con >50% valori null

    Args:
        df: DataFrame da processare.
        threshold: Soglia di null proportion (0.0 - 1.0) oltre la quale la riga viene scartata.

    Returns:
        DataFrame pulito.
    """
    logger.info(f"Dropping null rows with threshold {threshold}...")
    out_df = df.copy()
    
    # Calculate proportion of nulls per row
    null_proportions = out_df.isna().mean(axis=1)
    
    # Keep rows where null proportion is strictly less than threshold
    # Note: if threshold is 1.0, we want to drop rows that are *completely* null (proportion == 1.0)
    # If threshold is 0.5, drop rows where proportion >= 0.5
    if threshold == 1.0:
        mask = null_proportions < 1.0
    else:
        mask = null_proportions < threshold
        
    out_df = out_df[mask]
    
    logger.info(f"Dropped {len(df) - len(out_df)} rows due to nulls.")
    return out_df

def fill_nulls(
    df: pd.DataFrame,
    strategy: Literal["mean", "median", "mode", "constant"],
    value=None
) -> pd.DataFrame:
    """Riempie valori null con la strategia specificata.

    Args:
        df: DataFrame da processare.
        strategy: 'mean', 'median', 'mode' (per colonne individuali) o 'constant'.
        value: Il valore da usare se strategy='constant'.

    Returns:
        DataFrame con i null riempiti.
    """
    logger.info(f"Filling nulls with strategy {strategy}...")
    out_df = df.copy()
    
    if strategy == "constant":
        out_df = out_df.fillna(value)
    else:
        for col in out_df.columns:
            if out_df[col].isna().any():
                if strategy == "mean" and pd.api.types.is_numeric_dtype(out_df[col]):
                    val = out_df[col].mean()
                    out_df[col] = out_df[col].fillna(val)
                elif strategy == "median" and pd.api.types.is_numeric_dtype(out_df[col]):
                    val = out_df[col].median()
                    out_df[col] = out_df[col].fillna(val)
                elif strategy == "mode":
                    mode_s = out_df[col].mode()
                    if not mode_s.empty:
                        out_df[col] = out_df[col].fillna(mode_s[0])
                        
    return out_df

def flag_nulls(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """Aggiunge colonne booleane *_is_null per ogni colonna specificata.

    Args:
        df: DataFrame da processare.
        columns: Lista di colonne da testare. Se None, tutte le colonne con null.

    Returns:
        DataFrame con le flag *_is_null.
    """
    logger.info("Flagging nulls...")
    out_df = df.copy()
    
    cols_to_check = columns
    if cols_to_check is None:
        cols_to_check = [col for col in out_df.columns if out_df[col].isna().any()]
        
    for col in cols_to_check:
        if col in out_df.columns:
            out_df[f"{col}_is_null"] = out_df[col].isna()
            
    return out_df
