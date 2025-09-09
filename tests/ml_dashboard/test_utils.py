import pandas as pd
from fastclime.m4_dashboard import utils

def test_load_dataset_summary(monkeypatch):
    """
    Tests that load_dataset_summary constructs the correct query
    and returns the dataframe from read_duckdb.
    """
    mock_return_df = pd.DataFrame({"dataset": ["test_dataset"], "files": [123]})
    called_with = {}

    def mock_read_duckdb(query, params=None):
        called_with['query'] = query
        called_with['params'] = params
        return mock_return_df

    monkeypatch.setattr(utils, "read_duckdb", mock_read_duckdb)

    df = utils.load_dataset_summary()

    assert called_with['query'] == "SELECT name AS dataset, COUNT(*) files FROM datasets GROUP BY 1"
    assert called_with['params'] is None
    assert df.equals(mock_return_df)
