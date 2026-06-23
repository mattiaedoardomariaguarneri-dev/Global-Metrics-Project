"""
bootstrap_lookup.py
-------------------
Genera automaticamente source/countries_lookup.csv espanso a TUTTI i paesi
presenti in TUTTI e 4 i dataset WB con dati per il 2020.

Strategia:
  1. Legge i 4 CSV sorgente, estrae i codici ISO-3 con valore 2020 non-NaN.
  2. Calcola l'INTERSEZIONE (paesi con dati completi in tutti e 4 i dataset).
  3. Costruisce l'URI DBpedia a partire dal nome WB, con un dizionario di
     override per i casi in cui il nome WB differisce dal resource DBpedia
     (es. "Russian Federation" -> "Russia", "Korea, Rep." -> "South_Korea").
  4. Esclude aggregati regionali WB (non sono paesi sovrani).
  5. Salva il risultato in lookup_data/countries_lookup.csv.

Eseguire UNA SOLA VOLTA prima di run_pipeline.py.
"""

import os
import glob
import logging
import time
import re
from urllib.error import HTTPError
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Mappa: codice ISO-3 -> frammento esatto del resource DBpedia
# Necessaria quando il nome WB non corrisponde al titolo DBpedia
# ---------------------------------------------------------------------------
DBPEDIA_OVERRIDES = {
    # Nome WB                  -> frammento DBpedia
    "RUS": "Russia",                          # "Russian Federation"
    "KOR": "South_Korea",                     # "Korea, Rep."
    "PRK": "North_Korea",                     # "Korea, Dem. People's Rep."
    "IRN": "Iran",                            # "Iran, Islamic Rep."
    "EGY": "Egypt",                           # "Egypt, Arab Rep."
    "VEN": "Venezuela",                       # "Venezuela, RB"
    "YEM": "Yemen",                           # "Yemen, Rep."
    "LAO": "Laos",                            # "Lao PDR"
    "CZE": "Czech_Republic",                  # "Czechia"
    "SVK": "Slovakia",                        # "Slovak Republic"
    "KGZ": "Kyrgyzstan",                      # "Kyrgyz Republic"
    "MKD": "North_Macedonia",                 # "North Macedonia"
    "GMB": "The_Gambia",                      # "Gambia, The"
    "BHS": "The_Bahamas",                     # "Bahamas, The"
    "COD": "Democratic_Republic_of_the_Congo",# "Congo, Dem. Rep."
    "COG": "Republic_of_the_Congo",           # "Congo, Rep."
    "CIV": "Ivory_Coast",                     # "Cote d'Ivoire"
    "TLS": "East_Timor",                      # "Timor-Leste"
    "SWZ": "Eswatini",                        # "Eswatini"
    "TUR": "Turkey",                          # "Turkiye"
    "PSE": "Palestinian_territories",         # "West Bank and Gaza"
    "FSM": "Federated_States_of_Micronesia",  # "Micronesia, Fed. Sts."
    "STP": "S%C3%A3o_Tom%C3%A9_and_Pr%C3%ADncipe",  # "Sao Tome and Principe" (percent-encoded for DBpedia)
    "CPV": "Cape_Verde",                      # "Cabo Verde"
    "MDA": "Moldova",                         # "Moldova"
    "SYR": "Syria",                             # "Syrian Arab Republic"
    "VCT": "Saint_Vincent_and_the_Grenadines",
    "KNA": "Saint_Kitts_and_Nevis",
    "LCA": "Saint_Lucia",
    "ATG": "Antigua_and_Barbuda",
    "TTO": "Trinidad_and_Tobago",
    "TCA": "Turks_and_Caicos_Islands",
    "VGB": "British_Virgin_Islands",
    "MAC": "Macau",                           # "Macao SAR, China"
    "HKG": "Hong_Kong",                       # "Hong Kong SAR, China"
}

# Aggregati regionali WB che NON sono paesi sovrani (da escludere)
WB_NON_COUNTRY_CODES = {
    "AFE","AFW","ARB","CEB","CSS","EAP","EAR","EAS","ECA","ECS",
    "EMU","EUU","FCS","HIC","HPC","IBD","IBT","IDA","IDB","IDX",
    "LAC","LCN","LDC","LIC","LMC","LMY","LTE","MEA","MIC","MNA",
    "NAC","OED","OSS","PRE","PSS","PST","SAS","SSA","SSF","SST",
    "TEA","TEC","TLA","TMN","TSA","TSS","UMC","WLD","XZN",
    "INX",  # Not classified
}

DBPEDIA_BASE = "http://dbpedia.org/resource/"

def wb_name_to_dbpedia_fragment(name: str) -> str:
    """Converte un nome WB in un frammento DBpedia (best-effort)."""
    # Rimuovi suffissi tipo ", The" -> "The_"
    name = re.sub(r",\s*The$", "", name).strip()
    name = re.sub(r"^The\s+", "", name).strip()
    # Togli tutto dopo la virgola (es. "Korea, Rep." -> "Korea")
    # Solo se non è già gestito dagli override
    name = re.sub(r",.*$", "", name).strip()
    # Sostituisci spazi e caratteri speciali con underscore
    name = re.sub(r"[\s\-\(\)\.\']+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name

def canonical_name_from_override(code: str, wb_name: str) -> str:
    """Restituisce il nome canonico da usare nel CSV (leggibile, senza underscore)."""
    if code in DBPEDIA_OVERRIDES:
        return DBPEDIA_OVERRIDES[code].replace("_", " ")
    return wb_name_to_dbpedia_fragment(wb_name).replace("_", " ")

def build_lookup():
    files = {
        "pop":  glob.glob("raw_data/API_EN.POP.DNST*.csv")[0],
        "gdp":  glob.glob("raw_data/API_NY.GDP.PCAP.CD*.csv")[0],
        "life": glob.glob("raw_data/API_SP.DYN.LE00.IN*.csv")[0],
        "co2":  glob.glob("raw_data/API_EN.ATM.CO2E.PC*.csv")[0],
    }

    sets = {}
    code_to_wbname = {}

    for key, path in files.items():
        df = pd.read_csv(path, skiprows=4)
        df = df[df["2020"].notna()][["Country Name", "Country Code"]]
        df = df[~df["Country Code"].isin(WB_NON_COUNTRY_CODES)]
        codes = set(df["Country Code"].str.strip())
        sets[key] = codes
        for _, row in df.iterrows():
            code_to_wbname[row["Country Code"].strip()] = row["Country Name"].strip()

    # Intersezione: paesi con dati in TUTTI e 4 i dataset
    common_codes = sets["pop"] & sets["gdp"] & sets["life"] & sets["co2"]
    print(f"Paesi con dati completi in tutti e 4 i dataset: {len(common_codes)}")

    rows = []
    for code in sorted(common_codes):
        wb_name = code_to_wbname[code]
        if code in DBPEDIA_OVERRIDES:
            fragment = DBPEDIA_OVERRIDES[code]
        else:
            fragment = wb_name_to_dbpedia_fragment(wb_name)
        canonical = fragment.replace("_", " ")
        dbpedia_uri = DBPEDIA_BASE + fragment
        rows.append({
            "country_name": canonical,
            "country_code": code,
            "dbpedia_uri": dbpedia_uri,
        })

    lookup_df = pd.DataFrame(rows).sort_values("country_name").reset_index(drop=True)
    lookup_df.to_csv("lookup_data/countries_lookup.csv", index=False)
    print(f"Salvato lookup_data/countries_lookup.csv con {len(lookup_df)} paesi.")
    print(lookup_df[["country_name","country_code","dbpedia_uri"]].to_string())

if __name__ == "__main__":
    build_lookup()
