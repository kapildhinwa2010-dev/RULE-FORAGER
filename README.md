# 🔗 RULE-FORAGER

[![CI](https://github.com/kapildhinwa2010-dev/RULE-FORAGER/actions/workflows/ci.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/RULE-FORAGER/actions/workflows/ci.yml)
[![CodeQL](https://github.com/kapildhinwa2010-dev/RULE-FORAGER/actions/workflows/codeql.yml/badge.svg)](https://github.com/kapildhinwa2010-dev/RULE-FORAGER/actions/workflows/codeql.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Rules without a teacher

Give the forager only raw facts - atoms like (Japan, capital_of, Tokyo) -
and it hunts for structure on its own:

- 🔁 **Inverse relations** - if (a, p, b) then (b, q, a)
- 🤝 **Shared fillers** - many subjects pointing at the same object
- 📉 **Toy MDL scoring** - a rule earns its keep only if stating it once
  is cheaper than stating every atom it covers

## 🔍 What the demo finds

From 43 atoms (20 capital/country pairs in both directions + noise),
the forager rediscovers the capital_of ↔ country_of inverse rule
with support ≥ 15. Nobody told it that rule existed. 🐛✨

## 💻 Usage

    python rule_forager.py

Library:

    from rule_forager import demo_kb, forage
    report = forage(demo_kb())
    print(report["inverse_rules"])

## 🧪 Tests

    pytest -q

<details>
<summary>🔬 Honest limitations</summary>

- This is a **structure miner**, not full first-order logic induction: it finds
  inverse and shared-filler patterns, not arbitrary Horn clauses.
- MDL scoring here is a toy description-length heuristic (literal lengths +
  coverage), not a rigorous code-length model.

</details>

## ⚖️ License

MIT - see [LICENSE](LICENSE).
