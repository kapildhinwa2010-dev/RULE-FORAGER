import sys

sys.path.insert(0, ".")

from rule_forager import demo_kb, forage, mine_inverse


def test_inverse_rule_rediscovered():
    atoms = demo_kb()
    rules = mine_inverse(atoms, min_support=3)
    found = [r for r in rules if set(r["relations"]) == {"capital_of", "country_of"}]
    assert len(found) == 1
    assert found[0]["support"] >= 15


def test_inverse_rules_keep_their_own_relation_pair():
    atoms = []
    for i in range(3):
        atoms.extend([(f"a{i}", "r1", f"b{i}"), (f"b{i}", "s1", f"a{i}")])
        atoms.extend([(f"c{i}", "r2", f"d{i}"), (f"d{i}", "s2", f"c{i}")])

    rules = mine_inverse(atoms, min_support=3)
    pairs = {frozenset(rule["relations"]) for rule in rules}
    assert pairs == {frozenset(("r1", "s1")), frozenset(("r2", "s2"))}


def test_inverse_pair_deduplication_preserves_distinct_entity_types():
    atoms = [
        (1, "r", "x"), ("x", "s", 1),
        ("1", "r", "x"), ("x", "s", "1"),
    ]

    rules = mine_inverse(atoms, min_support=2)
    assert len(rules) == 1
    assert rules[0]["support"] == 2


def test_mdl_saved_positive():
    atoms = demo_kb()
    report = forage(atoms)
    for r in report["inverse_rules"]:
        assert r["mdl_saved"] > 0


def test_min_support_filters_noise():
    atoms = [("a", "r1", "b"), ("b", "r2", "a"), ("c", "r3", "d")]
    rules = mine_inverse(atoms, min_support=3)
    assert rules == []


def test_report_shape():
    report = forage(demo_kb())
    for k in ["n_atoms", "inverse_rules", "shared_filler_rules"]:
        assert k in report
    assert report["n_atoms"] == 43
