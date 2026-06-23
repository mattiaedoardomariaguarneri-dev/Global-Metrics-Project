import pytest
import pandas as pd
from pathlib import Path
from opendata_flowlib.enricher.enricher import enrich_with_country_id

def test_enrich_with_country_id(tmp_path):
    # Mock lookup CSV
    lookup_path = tmp_path / "countries.csv"
    lookup_df = pd.DataFrame({
        "country_name": ["Italy", "France"],
        "iso_alpha3": ["ITA", "FRA"]
    })
    lookup_df.to_csv(lookup_path, index=False)
    
    # Source DF
    df = pd.DataFrame({"country": ["italy", "FRANCE", "Unknown"]})
    
    # Enrich
    enriched = enrich_with_country_id(
        df,
        country_lookup_path=lookup_path,
        source_column="country",
        output_column="iso",
        country_label_column="country_name",
        country_code_column="iso_alpha3"
    )
    
    assert "iso" in enriched.columns
    result_list = enriched["iso"].tolist()
    assert result_list[0] == "ITA"
    assert result_list[1] == "FRA"
    assert pd.isna(result_list[2])
