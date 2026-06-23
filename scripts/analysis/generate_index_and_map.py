import os
import pandas as pd
import folium
import numpy as np
import requests
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)

def reorder_columns_uri_last(df: pd.DataFrame) -> pd.DataFrame:
    """Move dbpedia_uri to the last column for consistency across outputs."""
    if "dbpedia_uri" in df.columns:
        cols = [c for c in df.columns if c != "dbpedia_uri"] + ["dbpedia_uri"]
        return df[cols]
    return df

def calculate_gswi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola il Global Sustainability and Well-being Index (GSWI).
    Il calcolo si basa sulla normalizzazione (min-max scaling) dei 4 indicatori.
    Valori normalizzati da 0 a 1.
    """
    df = df.copy()
    
    # Rimuoviamo le righe che hanno NaN in almeno uno dei 4 indicatori
    metrics = ['gdp_per_capita', 'life_expectancy', 'co2_emissions', 'population_density']
    df_clean = df.dropna(subset=metrics).copy()
    
    # 1. GDP (log scale is better for income)
    df_clean['log_gdp'] = np.log1p(df_clean['gdp_per_capita'])
    gdp_min = df_clean['log_gdp'].min()
    gdp_max = df_clean['log_gdp'].max()
    df_clean['gdp_norm'] = (df_clean['log_gdp'] - gdp_min) / (gdp_max - gdp_min)
    
    # 2. Life Expectancy
    life_min = df_clean['life_expectancy'].min()
    life_max = df_clean['life_expectancy'].max()
    df_clean['life_norm'] = (df_clean['life_expectancy'] - life_min) / (life_max - life_min)
    
    # 3. CO2 Emissions (inverted: lower emissions = higher score)
    co2_min = df_clean['co2_emissions'].min()
    co2_max = df_clean['co2_emissions'].max()
    co2_norm_raw = (df_clean['co2_emissions'] - co2_min) / (co2_max - co2_min)
    df_clean['co2_norm_inv'] = 1 - co2_norm_raw
    
    # 4. Population Density (inverted: lower density = less pressure/higher score)
    # Using log scale because density can be extremely skewed (e.g., Monaco, Singapore)
    df_clean['log_pop'] = np.log1p(df_clean['population_density'])
    pop_min = df_clean['log_pop'].min()
    pop_max = df_clean['log_pop'].max()
    pop_norm_raw = (df_clean['log_pop'] - pop_min) / (pop_max - pop_min)
    df_clean['pop_norm_inv'] = 1 - pop_norm_raw
    
    # GSWI: Media dei 4 punteggi
    df_clean['gswi_index'] = (
        df_clean['gdp_norm'] + 
        df_clean['life_norm'] + 
        df_clean['co2_norm_inv'] + 
        df_clean['pop_norm_inv']
    ) / 4.0
    
    # Convertiamo in una scala da 0 a 100 per leggibilità
    df_clean['gswi_index'] = (df_clean['gswi_index'] * 100).round(2)
    
    # Reintegriamo nel dataframe originale
    # Chi non ha i dati completi avrà NaN
    df = df.merge(df_clean[['country_code', 'gswi_index']], on='country_code', how='left')
    
    return df

def generate_map():
    os.makedirs('charts', exist_ok=True)
    
    csv_path = 'processed/csv/global_metrics_2020.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return
        
    df = pd.read_csv(csv_path)
    df_with_index = calculate_gswi(df)
    df_with_index = reorder_columns_uri_last(df_with_index)
    
    # Save the updated dataframe
    out_csv = 'processed/csv/global_metrics_with_index_2020.csv'
    df_with_index.to_csv(out_csv, index=False)
    print(f"Dataset con indice salvato in {out_csv}")
    
    # Dropna per la mappa
    df_map = df_with_index.dropna(subset=['gswi_index'])
    
    # URL to the GeoJSON data containing world country geometries
    url = 'https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json'
    geo_data = requests.get(url).json()
    
    # Enrich the geo_data with our index so it can be used in tooltips
    gswi_dict = df_map.set_index('country_code')['gswi_index'].to_dict()
    for feature in geo_data['features']:
        cc = feature['id']
        val = gswi_dict.get(cc)
        feature['properties']['gswi_index'] = val if pd.notna(val) else 'Nessun dato'
    
    # Creiamo una mappa base (zoom sul mondo)
    m = folium.Map(location=[20, 0], zoom_start=2)
    
    # Aggiungiamo il livello Choropleth
    choro = folium.Choropleth(
        geo_data=geo_data,
        name='choropleth',
        data=df_map,
        columns=['country_code', 'gswi_index'],
        key_on='feature.id',  # L'ID nel GeoJSON è il codice ISO-3 (es. 'ITA')
        fill_color='YlGnBu',  # Giallo -> Verde -> Blu
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Global Sustainability and Well-being Index (GSWI)',
        nan_fill_color='white'
    ).add_to(m)
    
    # Aggiungiamo i tooltip interattivi
    tooltip = folium.GeoJsonTooltip(
        fields=['name', 'gswi_index'],
        aliases=['Paese:', 'Indice GSWI:']
    )
    choro.geojson.add_child(tooltip)
    
    folium.LayerControl().add_to(m)
    
    out_map = 'charts/world_map.html'
    m.save(out_map)
    print(f"Mappa generata con successo in {out_map}")

if __name__ == '__main__':
    generate_map()
