"""Unit tests for TGI scoring."""
import pytest
from src.treatment_gap.scoring import compute_tgi, DrugGeneEntry, TGIScore


SAMPLE_ENTRIES = [
    DrugGeneEntry("tacrolimus", "CYP3A5", "MXL", -2.84, "Strong"),
    DrugGeneEntry("azathioprine", "TPMT", "MXL", 0.0, "Strong"),
    DrugGeneEntry("azathioprine", "NUDT15", "MXL", 15.2, "Strong"),
    DrugGeneEntry("tacrolimus", "CYP3A5", "CEU", 0.0, "Strong"),  # baseline, skip
]


def test_ceu_excluded():
    scores = compute_tgi(SAMPLE_ENTRIES)
    pops = [s.population_code for s in scores]
    assert "CEU" not in pops


def test_tgi_non_negative():
    scores = compute_tgi(SAMPLE_ENTRIES)
    assert all(s.tgi >= 0 for s in scores)


def test_dedup_drug_gene():
    duped = SAMPLE_ENTRIES + [DrugGeneEntry("tacrolimus", "CYP3A5", "MXL", -5.0, "Strong")]
    scores = compute_tgi(duped)
    mxl = next(s for s in scores if s.population_code == "MXL")
    # CYP3A5 entry should appear once (dedup by drug|gene)
    assert mxl.n_drug_gene_pairs <= 3
