import logging
from typing import Dict, List

import pandas as pd

logger = logging.getLogger("opendata_flowlib.processor.aggregations")

def group_by(df: pd.DataFrame, by: List[str], agg: Dict[str, str]) -> pd.DataFrame:
    """Raggruppa per colonne e applica aggregazioni.

    Args:
        df: DataFrame da processare.
        by: Colonne di raggruppamento.
        agg: Dizionario colonna -> funzione di aggregazione.

    Returns:
        DataFrame aggregato.
    """
    logger.info(f"Grouping by {by} with aggregations {agg}...")
    return df.groupby(by).agg(agg).reset_index()

def pivot_table(
    df: pd.DataFrame,
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "mean"
) -> pd.DataFrame:
    """Crea una tabella pivot.

    Args:
        df: DataFrame da processare.
        index: Colonna da usare come indice.
        columns: Colonna da usare come nuove colonne.
        values: Colonna con i valori da aggregare.
        aggfunc: Funzione di aggregazione.

    Returns:
        Tabella pivot.
    """
    logger.info(f"Pivoting table: index={index}, columns={columns}, values={values}, aggfunc={aggfunc}")
    return df.pivot_table(index=index, columns=columns, values=values, aggfunc=aggfunc).reset_index()

def melt(df: pd.DataFrame, id_vars: List[str], value_vars: List[str]) -> pd.DataFrame:
    """Trasforma da formato wide a long.

    Args:
        df: DataFrame da processare.
        id_vars: Colonne identificative (da non squagliare).
        value_vars: Colonne da fondere.

    Returns:
        DataFrame in formato long (tidy).
    """
    logger.info(f"Melting data: id_vars={id_vars}, value_vars={value_vars}")
    return pd.melt(df, id_vars=id_vars, value_vars=value_vars)
