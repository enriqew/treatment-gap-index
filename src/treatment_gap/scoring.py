"""Compute Treatment Gap Index: composite PGx equity score per LATAM cohort."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


STRENGTH_WEIGHTS = {"Strong": 1.0, "Moderate": 0.7, "Optional": 0.4}
TRANSPLANT_DRUGS = {"tacrolimus", "azathioprine"}


@dataclass
class DrugGeneEntry:
    drug_name: str
    gene_symbol: str
    population_code: str
    delta_vs_baseline: float
    classification_strength: str


@dataclass
class TGIScore:
    population_code: str
    tgi: float
    n_drug_gene_pairs: int
    drug_breakdown: dict[str, float]


def compute_tgi(entries: Sequence[DrugGeneEntry]) -> list[TGIScore]:
    """
    TGI = weighted mean of |delta_vs_baseline| across transplant drug-gene pairs.
    Weight = classification_strength mapped to STRENGTH_WEIGHTS.
    """
    by_pop: dict[str, list[DrugGeneEntry]] = {}
    for e in entries:
        if e.drug_name not in TRANSPLANT_DRUGS:
            continue
        by_pop.setdefault(e.population_code, []).append(e)

    scores: list[TGIScore] = []
    for pop, pop_entries in by_pop.items():
        if pop == "CEU":
            continue

        # Deduplicate by drug|gene
        seen: set[str] = set()
        deduped: list[DrugGeneEntry] = []
        for e in pop_entries:
            key = f"{e.drug_name}|{e.gene_symbol}"
            if key not in seen:
                seen.add(key)
                deduped.append(e)

        total_weight = 0.0
        weighted_sum = 0.0
        breakdown: dict[str, float] = {}

        for e in deduped:
            w = STRENGTH_WEIGHTS.get(e.classification_strength, 0.5)
            weighted_sum += abs(e.delta_vs_baseline) * w
            total_weight += w
            key = f"{e.drug_name}·{e.gene_symbol}"
            breakdown[key] = abs(e.delta_vs_baseline)

        tgi = weighted_sum / total_weight if total_weight > 0 else 0.0

        scores.append(TGIScore(
            population_code=pop,
            tgi=round(tgi, 2),
            n_drug_gene_pairs=len(deduped),
            drug_breakdown=breakdown,
        ))

    return sorted(scores, key=lambda s: s.tgi, reverse=True)
