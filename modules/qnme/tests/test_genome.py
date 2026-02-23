# modules/qnme/tests/test_genome.py
from modules.qnme.genome import GenomeEngine

def test_genome_basic():
    g = GenomeEngine(window=10)
    for i in range(5):
        g.on_trade({"ts": i * 10, "size": i + 1, "price": 100 + i, "side": "B" if i % 2 == 0 else "S"})
    genome = g.compute_genome()
    assert "genome" in genome
    assert genome["genome"]["volume"] > 0
