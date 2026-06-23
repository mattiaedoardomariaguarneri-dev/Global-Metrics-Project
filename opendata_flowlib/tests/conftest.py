import pytest
import pandas as pd

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie", None],
        "Age": [25, 30, 35, None],
        "City": ["Roma", "Milano", "Roma", "Napoli"],
        "Salary": ["1.234,50", "2.345,00", "3.456,78", None],
    })

@pytest.fixture
def numeric_df():
    return pd.DataFrame({
        "a": [1, 2, 3, 4, 5],
        "b": [10, 20, 30, 40, 50],
        "c": [100, 200, 300, 400, 500],
    })

@pytest.fixture
def professor_columns_df():
    """DataFrame with column names like the professor's CSV."""
    return pd.DataFrame({
        "N": [1],
        "COMUNE": ["PALERMO"],
        "PROVINCIA": ["PA"],
        "POPOLAZIONE": ["663.401"],
        "S.R.R. DI COMPETENZA": ["SRR1"],
        "R.I. (TON)": ["1.234,56"],
        "R.D. (TON)": ["2.345,67"],
        "R.T. (TON)": ["3.580,23"],
        "R.D. (%)": ["65,43"],
        "R.C. (TON)": ["100,00"],
        "Extra D.M. 2016 (TON)": ["50,00"],
    })
