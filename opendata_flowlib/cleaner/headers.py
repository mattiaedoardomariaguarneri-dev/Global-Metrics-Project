import logging
import re
from typing import Literal

import pandas as pd

logger = logging.getLogger("opendata_flowlib.cleaner.headers")

def normalize_headers(df: pd.DataFrame, case: Literal["snake", "lower", "upper"] = "snake") -> pd.DataFrame:
    """Normalizza i nomi delle colonne di un DataFrame.

    Trasformazioni applicate:
    1. Sostituisce `(%)` con `_pct`
    2. Sostituisce `(TON)` con `_ton` (case insensitive)
    3. Rimuove altre parentesi e il loro contenuto
    4. Sostituisce spazi, trattini e caratteri non alfanumerici con underscore
    5. Converte nel case specificato
    6. Rimuove underscore multipli e trailing/leading underscore

    Args:
        df: DataFrame da processare.
        case: Case di destinazione ('snake', 'lower', 'upper').

    Returns:
        DataFrame con le colonne normalizzate.
    """
    logger.info("Normalizing headers...")
    new_columns = []
    
    for col in df.columns:
        original = str(col)
        # Handle specific cases first
        s = original.replace("(%)", "_pct")
        s = re.sub(r"\(\s*TON\s*\)", "_ton", s, flags=re.IGNORECASE)
        
        # Remove parenthetical content for anything else
        s = re.sub(r"\(.*?\)", "", s)
        
        # Replace spaces, hyphens, and any other non-alphanumeric (except _) with underscore
        s = re.sub(r"[^\w\s-]", "", s)  # Remove things like quotes, periods if they survived
        s = re.sub(r"[\s\-]+", "_", s)   # Replace spaces and hyphens with _
        
        # Apply case
        if case == "snake" or case == "lower":
            s = s.lower()
        elif case == "upper":
            s = s.upper()
            
        # Clean up multiple underscores and strip leading/trailing
        s = re.sub(r"_+", "_", s).strip("_")
        
        new_columns.append(s)
    
    # Actually we need to make sure we do exact matching for professor's example
    # N,COMUNE,PROVINCIA,POPOLAZIONE,"S.R.R. DI COMPETENZA","R.I. (TON)","R.D. (TON)","R.T. (TON)","R.D. (%)","R.C. (TON)","Extra D.M. 2016 (TON)"
    # should become:
    # n, comune, provincia, popolazione, s_r_r_di_competenza, r_i_ton, r_d_ton, r_t_ton, r_d_pct, r_c_ton, extra_d_m_2016_ton
    
    # Refined logic:
    new_cols_refined = []
    for col in df.columns:
        s = str(col)
        # 1. Replace specific known suffixes
        s = s.replace("(%)", "_pct")
        s = re.sub(r"\(\s*TON\s*\)", "_ton", s, flags=re.IGNORECASE)
        
        # 2. Remove any remaining parentheses and their contents
        s = re.sub(r"\(.*?\)", "", s)
        
        # 3. Replace dots with underscore (specifically for S.R.R. and R.I.)
        s = s.replace(".", "_")
        
        # 4. Replace spaces, hyphens, and non-alphanumeric with underscore
        s = re.sub(r"[^\w]", "_", s)
        
        # 5. Clean up multiple underscores and strip leading/trailing
        s = re.sub(r"_+", "_", s).strip("_")
        
        # 6. Apply case
        if case == "snake" or case == "lower":
            s = s.lower()
        elif case == "upper":
            s = s.upper()
            
        new_cols_refined.append(s)

    out_df = df.copy()
    out_df.columns = new_cols_refined
    logger.info("Headers normalized successfully.")
    return out_df

def rename_columns(df: pd.DataFrame, mapping: dict[str, str]) -> pd.DataFrame:
    """Rinomina le colonne usando un dizionario di mapping.

    Args:
        df: DataFrame da processare.
        mapping: Dizionario vecchio_nome -> nuovo_nome.

    Returns:
        DataFrame con colonne rinominate.
    """
    logger.info(f"Renaming columns using mapping: {mapping}")
    return df.rename(columns=mapping)

def drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rimuove colonne che iniziano con 'Unnamed:'.

    Args:
        df: DataFrame da processare.

    Returns:
        DataFrame senza le colonne Unnamed.
    """
    logger.info("Dropping 'Unnamed:' columns...")
    unnamed_cols = [c for c in df.columns if str(c).startswith("Unnamed:")]
    if unnamed_cols:
        logger.info(f"Dropped {len(unnamed_cols)} unnamed columns.")
        return df.drop(columns=unnamed_cols)
    return df.copy()
