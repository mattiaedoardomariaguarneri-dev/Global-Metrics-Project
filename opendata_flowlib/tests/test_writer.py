import pytest
import pandas as pd
from opendata_flowlib.writer.file_writer import save_csv

def test_save_csv(tmp_path, sample_df):
    file_path = tmp_path / "out.csv"
    
    # save_csv returns the unchanged DataFrame
    df = save_csv(sample_df, file_path)
    
    assert file_path.exists()
    pd.testing.assert_frame_equal(df, sample_df)
    
    # Read back to verify contents
    read_back = pd.read_csv(file_path)
    assert len(read_back) == len(sample_df)
