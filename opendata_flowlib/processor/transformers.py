import logging
from typing import List, Literal

import pandas as pd

logger = logging.getLogger("opendata_flowlib.processor.transformers")

def normalize_column(
    df: pd.DataFrame,
    column: str,
    method: Literal["minmax", "zscore"]
) -> pd.DataFrame:
    """Normalizza una colonna (min-max o z-score).

    Args:
        df: DataFrame da processare.
        column: Colonna da normalizzare.
        method: Metodo ('minmax' o 'zscore').

    Returns:
        DataFrame con la colonna normalizzata.
    """
    logger.info(f"Normalizing column {column} using method {method}")
    out_df = df.copy()
    
    if method == "minmax":
        min_val = out_df[column].min()
        max_val = out_df[column].max()
        if max_val > min_val:
            out_df[column] = (out_df[column] - min_val) / (max_val - min_val)
        else:
            out_df[column] = 0.0
    elif method == "zscore":
        mean_val = out_df[column].mean()
        std_val = out_df[column].std()
        if std_val > 0:
            out_df[column] = (out_df[column] - mean_val) / std_val
        else:
            out_df[column] = 0.0
            
    return out_df

def encode_categorical(
    df: pd.DataFrame,
    columns: List[str],
    method: Literal["onehot", "label"]
) -> pd.DataFrame:
    """Encoding di colonne categoriche (one-hot o label).

    Args:
        df: DataFrame da processare.
        columns: Colonne da encodare.
        method: Metodo ('onehot' o 'label').

    Returns:
        DataFrame encodato.
    """
    logger.info(f"Encoding columns {columns} using method {method}")
    out_df = df.copy()
    
    if method == "onehot":
        out_df = pd.get_dummies(out_df, columns=columns)
    elif method == "label":
        for col in columns:
            out_df[col] = out_df[col].astype('category').cat.codes
            
    return out_df

def add_column(df: pd.DataFrame, name: str, expression: str) -> pd.DataFrame:
    """Aggiunge una colonna calcolata con pandas eval.

    Args:
        df: DataFrame da processare.
        name: Nome della nuova colonna.
        expression: Espressione da valutare (es. 'price * quantity').

    Returns:
        DataFrame con la nuova colonna.
    """
    logger.info(f"Adding calculated column {name} with expression: {expression}")
    out_df = df.copy()
    out_df[name] = out_df.eval(expression)
    return out_df
