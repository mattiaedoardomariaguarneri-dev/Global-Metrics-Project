import pytest
import pandas as pd
from opendata_flowlib.processor.filters import filter_rows, select_columns, drop_columns
from opendata_flowlib.processor.aggregations import group_by, pivot_table, melt
from opendata_flowlib.processor.transformers import normalize_column, encode_categorical, add_column

def test_filter_rows():
    df = pd.DataFrame({"a": [1, 2, 3]})
    df = filter_rows(df, "a > 1")
    assert len(df) == 2
    assert df["a"].tolist() == [2, 3]

def test_select_columns():
    df = pd.DataFrame({"a": [1], "b": [2]})
    df = select_columns(df, ["a"])
    assert list(df.columns) == ["a"]

def test_drop_columns():
    df = pd.DataFrame({"a": [1], "b": [2]})
    df = drop_columns(df, ["a"])
    assert list(df.columns) == ["b"]

def test_group_by():
    df = pd.DataFrame({"group": ["A", "A", "B"], "val": [1, 2, 3]})
    df = group_by(df, ["group"], {"val": "sum"})
    assert df["val"].tolist() == [3, 3]

def test_pivot_table():
    df = pd.DataFrame({"A": ["foo", "foo"], "B": ["one", "two"], "C": [1, 2]})
    df = pivot_table(df, index="A", columns="B", values="C")
    assert "one" in df.columns and "two" in df.columns

def test_melt():
    df = pd.DataFrame({"id": [1], "val1": [10], "val2": [20]})
    df = melt(df, id_vars=["id"], value_vars=["val1", "val2"])
    assert len(df) == 2

def test_normalize_column():
    df = pd.DataFrame({"a": [0, 5, 10]})
    df = normalize_column(df, "a", "minmax")
    assert df["a"].tolist() == [0.0, 0.5, 1.0]

def test_encode_categorical():
    df = pd.DataFrame({"cat": ["A", "B", "A"]})
    df = encode_categorical(df, ["cat"], "onehot")
    assert "cat_A" in df.columns

def test_add_column():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    df = add_column(df, "c", "a + b")
    assert df["c"].tolist() == [4, 6]
