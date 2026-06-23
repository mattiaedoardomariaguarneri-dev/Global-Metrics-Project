import logging
from pathlib import Path
from typing import Union

import pandas as pd

logger = logging.getLogger("opendata_flowlib.writer.file_writer")

def save_csv(
    df: pd.DataFrame,
    path: Union[str, Path],
    encoding: str = "utf-8",
    separator: str = ",",
    index: bool = False,
    **kwargs
) -> pd.DataFrame:
    """Salva il DataFrame su file CSV e restituisce il DataFrame invariato.

    È un side-effect (scrittura file) ma il DataFrame passa through.

    Args:
        df: DataFrame da processare.
        path: Percorso del file CSV da scrivere.
        encoding: Encoding del file CSV.
        separator: Separatore di colonne.
        index: Se salvare o meno l'indice.
        **kwargs: Argomenti extra per to_csv.

    Returns:
        Il DataFrame inalterato.
    """
    try:
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path_obj, sep=separator, encoding=encoding, index=index, **kwargs)
        logger.info(f"save_csv: written {len(df)} rows to '{path}'")
    except Exception as e:
        logger.error(f"Error writing CSV to {path}: {e}")
        raise ValueError(f"Impossibile salvare il CSV: {e}")
        
    return df
