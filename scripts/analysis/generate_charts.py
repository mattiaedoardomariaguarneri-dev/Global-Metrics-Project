import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
os.chdir(PROJECT_ROOT)

def generate_charts():
    os.makedirs('charts', exist_ok=True)
    df = pd.read_csv('processed/csv/global_metrics_2020.csv')
    
    def add_selective_labels(df_filtered, x_col, y_col):
        # Trova top 3 e bottom 3 su asse Y, e top 3 su asse X
        top_y = df_filtered.nlargest(3, y_col)
        bottom_y = df_filtered.nsmallest(3, y_col)
        top_x = df_filtered.nlargest(3, x_col)
        to_label = pd.concat([top_y, bottom_y, top_x]).drop_duplicates(subset=['country_name'])
        
        for _, row in to_label.iterrows():
            plt.text(row[x_col], row[y_col], f" {row['country_name']}", fontsize=8, alpha=0.8, verticalalignment='bottom')

    # 1. Scatter: GDP vs CO2 (size: population_density)
    plt.figure(figsize=(10, 6))
    df_co2 = df.dropna(subset=['gdp_per_capita', 'co2_emissions']).copy()
    sns.scatterplot(data=df_co2, x='gdp_per_capita', y='co2_emissions', 
                    size='population_density', sizes=(20, 500), alpha=0.6, color='darkred')
    
    add_selective_labels(df_co2, 'gdp_per_capita', 'co2_emissions')
    
    plt.xscale('log')
    plt.title('GDP pro capite vs Emissioni di CO2 (Scala Logaritmica)\nLa dimensione dei cerchi rappresenta la Densità di Popolazione')
    plt.xlabel('GDP pro capite (US$)')
    plt.ylabel('Emissioni CO2 (tonnellate pro capite)')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig('charts/gdp_vs_co2.png')
    plt.close()

    # 2. Scatter: GDP vs Life Expectancy
    plt.figure(figsize=(10, 6))
    df_life = df.dropna(subset=['gdp_per_capita', 'life_expectancy']).copy()
    sns.scatterplot(data=df_life, x='gdp_per_capita', y='life_expectancy', 
                    color='darkblue', alpha=0.6)
    
    add_selective_labels(df_life, 'gdp_per_capita', 'life_expectancy')
    
    plt.xscale('log')
    plt.title('GDP pro capite vs Aspettativa di Vita (Scala Logaritmica)')
    plt.xlabel('GDP pro capite (US$)')
    plt.ylabel('Aspettativa di Vita (anni)')
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig('charts/gdp_vs_life.png')
    plt.close()
    
    print("Charts generated in charts/ directory.")

if __name__ == '__main__':
    generate_charts()
