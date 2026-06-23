import pytest
import pandas as pd
from opendata_flowlib.visualizer.charts import plot_bar, plot_line, plot_scatter, plot_histogram, plot_heatmap

def test_plot_bar():
    df = pd.DataFrame({"x": ["A", "B"], "y": [1, 2]})
    fig = plot_bar(df, "x", "y")
    assert fig is not None

def test_plot_line():
    df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
    fig = plot_line(df, "x", "y")
    assert fig is not None

def test_plot_scatter():
    df = pd.DataFrame({"x": [1, 2], "y": [1, 2]})
    fig = plot_scatter(df, "x", "y")
    assert fig is not None

def test_plot_histogram():
    df = pd.DataFrame({"x": [1, 2, 2, 3]})
    fig = plot_histogram(df, "x")
    assert fig is not None

def test_plot_heatmap():
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    fig = plot_heatmap(df)
    assert fig is not None
