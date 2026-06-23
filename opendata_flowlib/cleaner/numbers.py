import logging
from typing import Iterable, List, Optional

import pandas as pd

logger = logging.getLogger("opendata_flowlib.cleaner.numbers")

def strip_column_suffixes(
    df: pd.DataFrame,
    suffixes: Iterable[str] = ("_ton",),
    percent_suffix: str = "_pct"
) -> pd.DataFrame:
    """Rimuove suffissi di unità dai nomi delle colonne.

    Attenzione: se la colonna termina con percent_suffix, viene ignorata e non modificata.

    Args:
        df: DataFrame da processare.
        suffixes: Suffissi da rimuovere se presenti alla fine del nome.
        percent_suffix: Suffisso che "protegge" la colonna da ulteriori modifiche.

    Returns:
        DataFrame con i nomi delle colonne modificati.
    """
    logger.info("Stripping column suffixes...")
    new_cols = []
    for col in df.columns:
        s = str(col)
        if s.endswith(percent_suffix):
            new_cols.append(s)
            continue
            
        modified = s
        for suffix in suffixes:
            if modified.endswith(suffix):
                modified = modified[:-len(suffix)]
                
        new_cols.append(modified)

    out_df = df.copy()
    out_df.columns = new_cols
    return out_df

def normalize_numeric_values(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    thousand_separators: Iterable[str] = (".", " "),
    infer_numeric: bool = False,
    strip_percent: bool = True,
) -> pd.DataFrame:
    """Normalizza valori numerici nelle colonne specificate.

    Operazioni:
    - Rimuove separatori di migliaia (punto, spazio)
    - Converte virgola decimale italiana in punto
    - Rimuove il simbolo % se strip_percent=True
    - Se infer_numeric=True, tenta pd.to_numeric con errors='coerce'

    Args:
        df: DataFrame da processare.
        columns: Lista di colonne da normalizzare. Se None, tutte.
        thousand_separators: Separatori di migliaia da rimuovere.
        infer_numeric: Se True, tenta conversione a numeric.
        strip_percent: Se True, rimuove il simbolo %.

    Returns:
        DataFrame con i valori numerici normalizzati.
    """
    logger.info("Normalizing numeric values...")
    out_df = df.copy()
    
    cols_to_process = columns if columns is not None else out_df.columns
    
    for col in cols_to_process:
        if col not in out_df.columns:
            continue
            
        # We only apply string operations if the column is actually of object/string type
        if out_df[col].dtype == "object":
            # Strip percentage
            if strip_percent:
                out_df[col] = out_df[col].astype(str).str.replace("%", "", regex=False)
            
            # Remove thousand separators
            for sep in thousand_separators:
                # We need to be careful with dots. If it's an Italian number like "1.234,56", dot is thousand.
                # If it's already "1234.56", removing dot breaks it. 
                # The logic expected by the prompt: "Converte virgola decimale italiana in punto, rimuove separatori migliaia (punto, spazio)"
                out_df[col] = out_df[col].astype(str).str.replace(sep, "", regex=False)
                
            # Replace comma with dot
            out_df[col] = out_df[col].astype(str).str.replace(",", ".", regex=False)
            
            # Handle empty strings that might have resulted from above operations
            out_df[col] = out_df[col].replace(r"^\s*$", None, regex=True)
            # Remove string "nan" which might happen during casting
            out_df[col] = out_df[col].replace("nan", None)
            
        if infer_numeric:
            out_df[col] = pd.to_numeric(out_df[col], errors='coerce')
            
    return out_df
