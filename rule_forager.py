"""RULE-FORAGER: rediscover rules from facts alone - no teacher, no labels.

Given only a knowledge base of atoms (subject, relation, object), the forager
hunts for structure: inverse relations and shared fillers. Rules are scored
by description length saved (a toy MDL principle): a rule is worth keeping
only if replacing the atoms it covers costs more bits than stating the rule
once.

Pure Python. No dependencies. No training. Bounded evaluation.
"""

__version__ = "0.1.0"

import json
from collections import defaultdict


def mine_inverse(atoms, min_support=3):
    """Find canonical relation pairs (p, q) where (a, p, b) and (b, q, a) co-occur.

    Each unordered subject pair is visited once, and each relation pair is
    canonicalized (sorted), so an inverse rule is reported exactly once.
    """
    lookup = set(atoms)
    rev_rels = defaultdict(set)
    for s, r, o in lookup:
        rev_rels[(s, o)].add(r)

    counts = defaultdict(int)
    seen_pairs = set()
    for a, p, b in atoms:
        key = tuple(sorted([str(a), str(b)]))
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        for q in rev_rels.get((b, a), set()):
            pair = tuple(sorted([p, q]))
            counts[pair] += 1

    rules = []
    for (p, q), support in counts.items():
        if support >= min_support:
            saved = 2 * support - (len(p) + len(q) + 1)
            if saved > 0:
                rules.append({"rule": "inverse", "relations": list(pair), "support": support, "mdl_saved": saved})
    return sorted(rules, key=lambda r: -r["support"])


def mine_shared_fillers(atoms, min_support=3):
    """Find relation + filler patterns shared by many subjects."""
    by_pair = defaultdict(set)
    for a, p, b in atoms:
        by_pair[(p, b)].add(a)
    rules = []
    for (p, b), subjects in by_pair.items():
        if len(subjects) >= min_support:
            rules.append({"rule": "shared_filler", "relation": p, "filler": b, "support": len(subjects)})
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
