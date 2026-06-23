import pytest
import pandas as pd
from opendata_flowlib.pipeline.pipeline import Pipeline, compose, step
from opendata_flowlib.reader.file_reader import read_csv
from opendata_flowlib.processor.filters import filter_rows

def test_pipeline_basic(tmp_path):
    # Prepare data
    file_path = tmp_path / "test.csv"
    pd.DataFrame({"a": [1, 2, 3]}).to_csv(file_path, index=False)
    
    # Run pipeline
    result = (
        Pipeline()
        .read(read_csv, file_path)
        .process(filter_rows, condition="a > 1")
        .run()
    )
    
    assert len(result.df) == 2
    assert len(result.steps_log) == 2
    assert result.steps_log[0].step_name == "read_csv"
    assert result.steps_log[1].step_name == "filter_rows"

def test_pipeline_error_raise(tmp_path):
    file_path = tmp_path / "test.csv"
    pd.DataFrame({"a": [1]}).to_csv(file_path, index=False)
    
    pipeline = Pipeline(on_error="raise").read(read_csv, file_path).process(filter_rows, condition="bad syntax")
    with pytest.raises(Exception):
        pipeline.run()

def test_pipeline_error_skip(tmp_path):
    file_path = tmp_path / "test.csv"
    pd.DataFrame({"a": [1]}).to_csv(file_path, index=False)
    
    result = (
        Pipeline(on_error="skip")
        .read(read_csv, file_path)
        .process(filter_rows, condition="bad syntax")
        .run()
    )
    
    assert len(result.df) == 1
    assert len(result.errors) == 1

def test_compose_and_step():
    def add_one(df, col):
        out = df.copy()
        out[col] = out[col] + 1
        return out
        
    df = pd.DataFrame({"a": [1, 2]})
    pipeline_fn = compose(
        step(add_one, col="a"),
        step(add_one, col="a")
    )
    
    res = pipeline_fn(df)
    assert res["a"].tolist() == [3, 4]
