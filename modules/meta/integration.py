# modules/meta/integration.py
from modules.meta.model import MetaModel
import numpy as np
from typing import Dict, Any

def add_meta_probs_to_df(df, mm: MetaModel, feature_cols: list):
    # df: pandas DataFrame; mm: MetaModel
    X = df[feature_cols].to_numpy()
    probs = mm.predict_proba(X)  # if mm returns list/dict depending on input; adapt
    # convert to DataFrame columns p_buy/p_sell/p_hold
    if isinstance(probs, dict):
        # single sample case
        for k,v in probs.items():
            df[k] = v
    else:
        # list of dicts or 2D array
        import pandas as pd
        pdp = pd.DataFrame(probs)
        # standardize names to p_buy/p_sell/p_hold
        df["p_buy"] = pdp.get("p_buy", 0.0)
        df["p_sell"] = pdp.get("p_sell", 0.0)
        df["p_hold"] = pdp.get("p_hold", 0.0)
    return df
