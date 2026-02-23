# modules/qnme/tests/test_mutation.py
from modules.qnme.mutation import gaussian_mutate, crossover

def test_mutation_and_crossover():
    p1 = {"window": 20, "z_entry": 1.5, "size": 1}
    p2 = {"window": 30, "z_entry": 1.0, "size": 2}
    child = gaussian_mutate(p1, sigma=0.01)
    assert "window" in child
    c = crossover(p1, p2)
    assert "window" in c
