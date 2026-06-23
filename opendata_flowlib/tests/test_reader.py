import pytest
import pandas as pd
from pathlib import Path
from opendata_flowlib.reader.file_reader import read_csv, read_excel, read_json, read_parquet

def test_read_csv(tmp_path, sample_df):
    file_path = tmp_path / "test.csv"
    sample_df.to_csv(file_path, index=False)
    
    df = read_csv(file_path)
    pd.testing.assert_frame_equal(df, sample_df)

def test_read_csv_not_found():
    with pytest.raises(FileNotFoundError):
        read_csv("nonexistent_file.csv")

def test_read_excel(tmp_path, sample_df):
    file_path = tmp_path / "test.xlsx"
    sample_df.to_excel(file_path, index=False)
    
    df = read_excel(file_path)
    pd.testing.assert_frame_equal(df, sample_df)

def test_read_json(tmp_path, sample_df):
    file_path = tmp_path / "test.json"
    sample_df.to_json(file_path, orient="records")
    
    df = read_json(file_path)
    pd.testing.assert_frame_equal(df, sample_df)

def test_read_parquet(tmp_path, sample_df):
    file_path = tmp_path / "test.parquet"
    sample_df.to_parquet(file_path, index=False)
    
    df = read_parquet(file_path)
    pd.testing.assert_frame_equal(df, sample_df)
