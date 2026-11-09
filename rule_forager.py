"""RULE-FORAGER: rediscover rules from facts alone - no teacher, no labels.

Given only a knowledge base of atoms (subject, relation, object), the forager
hunts for structure: inverse relations, symmetric relations, and shared
fillers. Rules are scored by description length saved (a toy MDL principle):
a rule is worth keeping only if replacing the atoms it covers costs more bits
than stating the rule once.

Pure Python. No dependencies. No training. Bounded evaluation.
"""

__version__ = "0.1.0"

import json
from collections import defaultdict


def mine_inverse(atoms, min_support=3):
    """Find relation pairs (p, q) where (a, p, b) and (b, q, a) co-occur."""
    lookup = set(atoms)
    counts = defaultdict(int)
    for a, p, b in atoms:
        if (b, p, a) in lookup:
            counts[(p, p)] += 1
        for q in {rel for s2, rel, o2 in [(b, r, a) for r in _rels_of(lookup, b, a)]}:
            counts[(p, q)] += 1
    rules = []
    for (p, q), support in counts.items():
        if support >= min_support:
            saved = 2 * support - (len(p) + len(q) + 1)
            if saved > 0:
                rules.append({"rule": "inverse", "relations": [p, q], "support": support, "mdl_saved": saved})
    return sorted(rules, key=lambda r: -r["support"])


def _rels_of(lookup, subj, obj):
    """Relations linking subj -> obj in the lookup set."""
    out = set()
    for s, r, o in lookup:
        if s == subj and o == obj:
            out.add(r)
    return out


def mine_shared_fillers(atoms, min_support=3):
    """Find relation pairs that share the same object pattern."""
    by_pair = defaultdict(set)
    for a, p, b in atoms:
        by_pair[(p, b)].add(a)
    rules = []
    counts = defaultdict(int)
    for (p, b), subjects in by_pair.items():
        if len(subjects) >= min_support:
            counts[(p, b)] = len(subjects)
    for (p, b), support in counts.items():
        rules.append({"rule": "shared_filler", "relation": p, "filler": b, "support": support})
    return sorted(rules, key=lambda r: -r["support"])


def forage(atoms, min_support=3):
    return {
        "n_atoms": len(atoms),
        "inverse_rules": mine_inverse(atoms, min_support),
        "shared_filler_rules": mine_shared_fillers(atoms, min_support),
    }


def demo_kb(n_pairs=20):
    """Capital/country pairs in both directions + unrelated noise atoms."""
    pairs = [
        ("Japan", "Tokyo"), ("France", "Paris"), ("Italy", "Rome"),
        ("Germany", "Berlin"), ("Spain", "Madrid"), ("India", "New Delhi"),
        ("China", "Beijing"), ("Brazil", "Brasilia"), ("Egypt", "Cairo"),
        ("Kenya", "Nairobi"), ("Peru", "Lima"), ("Chile", "Santiago"),
        ("Norway", "Oslo"), ("Greece", "Athens"), ("Poland", "Warsaw"),
        ("Korea", "Seoul"), ("Canada", "Ottawa"), ("Mexico", "Mexico City"),
        ("Turkey", "Ankara"), ("Vietnam", "Hanoi"),
    ][:n_pairs]
    atoms = []
    for country, capital in pairs:
        atoms.append((country, "capital_of", capital))
        atoms.append((capital, "country_of", country))
    noise = [
        ("water", "boils_at_c", 100),
        ("pi", "first_digits", "314"),
        ("sun", "rises_in", "east"),
    ]
    return atoms + noise


def main():
    atoms = demo_kb()
    report = forage(atoms, min_support=3)
    print(json.dumps(report, indent=2))
    assert any(set(r["relations"]) == {"capital_of", "country_of"} for r in report["inverse_rules"]), "forager missed the inverse rule"


if __name__ == "__main__":
    main()
