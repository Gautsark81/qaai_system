# modules/qnme/tests/test_genome_numba.py
from modules.qnme.genome_numba import GenomeNumPyEngine

def test_genome_numpy_basic():
    g = GenomeNumPyEngine(window=100)
    for i in range(30):
        g.on_trade({"ts": i*10, "price": 100 + i, "size": i%5 + 1, "side": "B" if i%2==0 else "S", "spread": 0.01})
    out = g.compute_genome()
    assert "genome" in out
    assert out["genome"]["n_trades"] == 30
    assert out["genome"]["volume"] > 0
