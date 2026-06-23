import logging
from pathlib import Path
from typing import Optional, Union

import pandas as pd

logger = logging.getLogger("opendata_flowlib.enricher")

def enrich_with_country_id(
    df: pd.DataFrame,
    country_lookup_path: Union[str, Path],
    source_column: str,
    output_column: str = "iso_alpha3",
    country_label_column: str = "country_name",
    country_code_column: str = "iso_alpha3",
    separator: str = ",",
    encoding: str = "utf-8",
    log_path: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    """Arricchisce il DataFrame aggiungendo il codice ISO della nazione.

    Comportamento:
    1. Legge il CSV di lookup con le colonne almeno: country_name, iso_alpha3
    2. Fa il match case-insensitive tra df[source_column] e lookup[country_label_column]
    3. Aggiunge la colonna output_column al DataFrame
    4. Logga su file (se log_path è fornito) e su logging standard i risultati

    Args:
        df: DataFrame sorgente.
        country_lookup_path: Percorso del CSV di lookup.
        source_column: Colonna del DF sorgente contenente il nome della nazione.
        output_column: Colonna del codice da aggiungere al DF.
        country_label_column: Colonna nel lookup con il nome testuale della nazione.
        country_code_column: Colonna nel lookup con il codice della nazione.
        separator: Separatore del CSV di lookup.
        encoding: Encoding del CSV di lookup.
        log_path: Percorso file dove salvare il log di enrichment.

    Returns:
        DataFrame arricchito con la nuova colonna.
    """
    logger.info(f"enrich_with_country_id: loading lookup {country_lookup_path}")
    
    try:
        lookup_df = pd.read_csv(country_lookup_path, sep=separator, encoding=encoding)
    except Exception as e:
        logger.error(f"Impossibile leggere il file di lookup: {e}")
        raise ValueError(f"Impossibile leggere il file di lookup: {e}")

    # Make mapping dictionary (case-insensitive)
    if country_label_column not in lookup_df.columns or country_code_column not in lookup_df.columns:
        raise ValueError(f"Colonne lookup mancanti: attese {country_label_column} e {country_code_column}")
        
    lookup_map = {
        str(row[country_label_column]).strip().upper(): str(row[country_code_column])
        for _, row in lookup_df.iterrows()
    }

    out_df = df.copy()
    
    # Apply mapping
    source_values_upper = out_df[source_column].astype(str).str.strip().str.upper()
    out_df[output_column] = source_values_upper.map(lookup_map)

    # Calculate metrics
    total_rows = len(out_df)
    enriched_rows = out_df[output_column].notna().sum()
    missing_countries = out_df[out_df[output_column].isna()][source_column].dropna().unique().tolist()

    # Logging results
    msg_success = f"enrich_with_country_id: enriched {enriched_rows}/{total_rows} rows from '{Path(country_lookup_path).name}' using '{country_label_column}'"
    logger.info(msg_success)
    
    msg_warning = ""
    if missing_countries:
        msg_warning = f"enrich_with_country_id: {len(missing_countries)} countries non trovati in '{Path(country_lookup_path).name}': {missing_countries[:10]}{'...' if len(missing_countries) > 10 else ''}"
        logger.warning(msg_warning)

    # File logging
    if log_path:
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(f"[INFO] {msg_success}\n")
            if missing_countries:
                f.write(f"[WARNING] {msg_warning}\n")
                
    return out_df
