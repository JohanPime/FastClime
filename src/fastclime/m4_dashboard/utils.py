from functools import lru_cache
import duckdb
import pandas as pd
from pathlib import Path
from fastclime.config import settings

DB_PATH = settings.DATA_DIR / "catalog.db"

@lru_cache(maxsize=8)
def read_duckdb(query: str, params: tuple | None = None) -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute(query, params or ()).df()
    con.close()
    return df

def load_dataset_summary():
    return read_duckdb("SELECT name AS dataset, COUNT(*) files FROM datasets GROUP BY 1")
