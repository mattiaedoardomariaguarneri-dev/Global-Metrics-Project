import os
import glob
import logging
from pathlib import Path

import pandas as pd

from opendata_flowlib.pipeline.pipeline import Pipeline
from opendata_flowlib.reader.file_reader import read_csv
from opendata_flowlib.cleaner.headers import normalize_headers, drop_unnamed_columns
from opendata_flowlib.cleaner.nulls import drop_null_rows
from opendata_flowlib.processor.aggregations import melt
from opendata_flowlib.processor.filters import select_columns, filter_rows
from opendata_flowlib.enricher.enricher import enrich_with_country_id
from opendata_flowlib.writer.file_writer import save_csv

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("run_pipeline")

LOOKUP_PATH = "lookup_data/countries_lookup.csv"

def get_latest_csv(prefix: str, directory: str = "raw_data") -> str:
    """Find the CSV file in the directory that starts with the given prefix."""
    files = glob.glob(os.path.join(directory, f"{prefix}*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV found for prefix {prefix} in {directory}")
    return files[0]

def reorder_columns_uri_last(df: pd.DataFrame) -> pd.DataFrame:
    """Sposta dbpedia_uri come ultima colonna del DataFrame."""
    if "dbpedia_uri" in df.columns:
        cols = [c for c in df.columns if c != "dbpedia_uri"] + ["dbpedia_uri"]
        return df[cols]
    return df

def normalize_country_name(df: pd.DataFrame, lookup_path: str = LOOKUP_PATH) -> pd.DataFrame:
    """Sostituisce il country_name del dataset WB con il nome canonico del lookup.

    Questo step è necessario perché la World Bank usa nomi come "Russian Federation"
    o "Korea, Rep." che non coincidono con i nomi nel lookup né tra dataset diversi.
    Facendo il join per codice ISO-3 e poi normalizzando il nome, tutti i dataset
    usano lo stesso nome canonico (es. "Russia", "South Korea"), garantendo che il
    merge finale per country_name funzioni correttamente.
    """
    lookup = pd.read_csv(lookup_path)
    code_to_name = dict(zip(
        lookup["country_code"].str.strip(),
        lookup["country_name"].str.strip()
    ))
    out = df.copy()
    out["country_name"] = out["country_code"].map(code_to_name).fillna(out["country_name"])
    return out

def process_dataset(filepath: str, indicator_name: str, output_path: str):
    logger.info(f"Processing {indicator_name} from {filepath}...")

    # Custom step to rename the value column to the indicator name
    def rename_value_col(df, old_name, new_name):
        return df.rename(columns={old_name: new_name})

    pipeline = (
        Pipeline()
        .read(read_csv, filepath, skiprows=4)          # WB CSVs have 4 rows of metadata
        .clean(drop_unnamed_columns)
        .clean(normalize_headers, case="snake")
        .process(select_columns, columns=["country_name", "country_code", "2020"])
        .process(filter_rows, condition="`2020`.notna()")
        .process(rename_value_col, old_name="2020", new_name=indicator_name)
        # --- Arricchimento per codice ISO-3 (robusto a varianti di nome WB) ---
        .process(
            enrich_with_country_id,
            country_lookup_path=LOOKUP_PATH,
            source_column="country_code",         # join key: codice ISO-3
            output_column="dbpedia_uri",
            country_label_column="country_code",  # colonna chiave nel lookup
            country_code_column="dbpedia_uri",    # colonna valore da copiare
            log_path=f"lookup_data/{indicator_name}_enrich_log.txt"
        )
        .process(filter_rows, condition="dbpedia_uri.notna()")   # Solo paesi nel lookup
        .process(normalize_country_name, lookup_path=LOOKUP_PATH) # Nome canonico uniforme
        .process(reorder_columns_uri_last)           # dbpedia_uri in ultima posizione
        .process(save_csv, path=output_path, index=False)
    )

    result = pipeline.run()
    if result.errors:
        logger.error(f"Errors occurred during {indicator_name} pipeline:")
        for err in result.errors:
            logger.error(err)

    return result.df

def main():
    os.makedirs("processed/csv", exist_ok=True)

    # Find files
    pop_density_file = get_latest_csv("API_EN.POP.DNST")
    gdp_file = get_latest_csv("API_NY.GDP.PCAP.CD")
    life_exp_file = get_latest_csv("API_SP.DYN.LE00.IN")
    co2_file = get_latest_csv("API_EN.ATM.CO2E.PC")

    # Process each
    df_pop  = process_dataset(pop_density_file,  "population_density", "processed/csv/pop_density_2020.csv")
    df_gdp  = process_dataset(gdp_file,          "gdp_per_capita",     "processed/csv/gdp_2020.csv")
    df_life = process_dataset(life_exp_file,      "life_expectancy",    "processed/csv/life_exp_2020.csv")
    df_co2  = process_dataset(co2_file,           "co2_emissions",      "processed/csv/co2_2020.csv")

    logger.info("All pipelines completed successfully.")

    # Merge into a single dataframe — join on country_code + dbpedia_uri.
    # country_name è ora normalizzato in tutti i dataset, quindi il join su tre chiavi
    # è sicuro e non crea righe duplicate per varianti di nome (es. Russian Federation).
    logger.info("Merging datasets into a single file...")
    merge_keys = ["country_name", "country_code", "dbpedia_uri"]
    merged = df_pop.merge(df_gdp,  on=merge_keys, how="outer")
    merged = merged.merge(df_life, on=merge_keys, how="outer")
    merged = merged.merge(df_co2,  on=merge_keys, how="outer")
    merged = merged.sort_values("country_name").reset_index(drop=True)
    merged = reorder_columns_uri_last(merged)          # dbpedia_uri in ultima posizione

    save_csv(merged, "processed/csv/global_metrics_2020.csv", index=False)
    logger.info(f"Merged dataset saved — {len(merged)} paesi in processed/csv/global_metrics_2020.csv")

if __name__ == "__main__":
    main()
