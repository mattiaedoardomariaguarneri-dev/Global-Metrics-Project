import pytest
import pandas as pd
from opendata_flowlib.cleaner.headers import normalize_headers, rename_columns, drop_unnamed_columns
from opendata_flowlib.cleaner.numbers import strip_column_suffixes, normalize_numeric_values
from opendata_flowlib.cleaner.types import infer_and_cast_types, cast_column, parse_dates
from opendata_flowlib.cleaner.nulls import drop_null_rows, fill_nulls, flag_nulls
from opendata_flowlib.cleaner.dedup import drop_duplicates, flag_duplicates

def test_normalize_headers_professor(professor_columns_df):
    df = normalize_headers(professor_columns_df, case="snake")
    expected_cols = [
        "n", "comune", "provincia", "popolazione", "s_r_r_di_competenza",
        "r_i_ton", "r_d_ton", "r_t_ton", "r_d_pct", "r_c_ton", "extra_d_m_2016_ton"
    ]
    assert list(df.columns) == expected_cols

def test_normalize_headers_upper():
    df = pd.DataFrame({"First Name": [1], "AGE (years)": [2]})
    df = normalize_headers(df, case="upper")
    assert list(df.columns) == ["FIRST_NAME", "AGE"]

def test_rename_columns():
    df = pd.DataFrame({"A": [1], "B": [2]})
    df = rename_columns(df, {"A": "X"})
    assert list(df.columns) == ["X", "B"]

def test_drop_unnamed_columns():
    df = pd.DataFrame({"A": [1], "Unnamed: 0": [2]})
    df = drop_unnamed_columns(df)
    assert list(df.columns) == ["A"]

def test_strip_column_suffixes():
    df = pd.DataFrame(columns=["r_i_ton", "r_d_pct", "extra_ton"])
    df = strip_column_suffixes(df, suffixes=("_ton",), percent_suffix="_pct")
    assert list(df.columns) == ["r_i", "r_d_pct", "extra"]

def test_normalize_numeric_values():
    df = pd.DataFrame({"val": ["1.234,56", "1.000", "50,5%"]})
    df = normalize_numeric_values(df, columns=["val"], infer_numeric=True)
    assert df["val"].tolist() == [1234.56, 1000.0, 50.5]

def test_infer_and_cast_types():
    df = pd.DataFrame({"a": ["1", "2"], "b": ["1.5", "2.5"]})
    df = infer_and_cast_types(df)
    assert pd.api.types.is_numeric_dtype(df["a"])

def test_cast_column():
    df = pd.DataFrame({"a": ["1", "2"]})
    df = cast_column(df, "a", "int64")
    assert df["a"].dtype == "int64"

def test_parse_dates():
    df = pd.DataFrame({"d": ["2020-01-01", "2020-01-02"]})
    df = parse_dates(df, ["d"])
    assert pd.api.types.is_datetime64_any_dtype(df["d"])

def test_drop_null_rows():
    df = pd.DataFrame({"a": [1, None, None], "b": [2, 3, None]})
    df = drop_null_rows(df, threshold=1.0)
    assert len(df) == 2  # solo riga tutta nulla viene droppata

def test_fill_nulls():
    df = pd.DataFrame({"a": [1, None, 3]})
    df = fill_nulls(df, strategy="constant", value=0)
    assert df["a"].tolist() == [1, 0, 3]

def test_flag_nulls():
    df = pd.DataFrame({"a": [1, None]})
    df = flag_nulls(df)
    assert "a_is_null" in df.columns
    assert df["a_is_null"].tolist() == [False, True]

def test_drop_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2]})
    df = drop_duplicates(df)
    assert len(df) == 2

def test_flag_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2]})
    df = flag_duplicates(df)
    assert "_is_duplicate" in df.columns
    assert df["_is_duplicate"].tolist() == [True, True, False]
