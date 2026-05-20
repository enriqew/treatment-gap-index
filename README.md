# Treatment Gap Index

A composite pharmacogenomic equity index that quantifies how far standard CPIC-derived
prescribing guidelines are from being optimal for Latin American transplant populations.

## What is the TGI?

The Treatment Gap Index (TGI) is a single, interpretable score per cohort that aggregates
divergence from the European clinical baseline across all transplant-relevant pharmacogenes.
A TGI of 0 means the population responds identically to the European baseline used in most
CPIC guidelines. Higher values indicate greater divergence — i.e., a larger fraction of the
cohort would receive sub-optimal dosing under standard protocols.

**Formula:**

```
TGI = Σ(|delta_vs_baseline_i| × w_i) / Σ(w_i)

where:
  delta_vs_baseline_i  = percentage-point difference from CEU baseline for pair i
  w_i                  = 1.0 if CPIC classification is Strong, 0.7 if Moderate
```

## Inputs

All inputs are Gold-layer artifacts produced by the
[pgx-latam-atlas](https://github.com/enriqew/pgx-latam-atlas) pipeline.

| Artifact | File | Key fields used |
|---|---|---|
| Drug impact summary | `drug_impact_summary.json` | `drug_name`, `gene_symbol`, `population_code`, `percentage_requiring_change`, `baseline_ceu_percentage`, `delta_vs_baseline`, `classification_strength` |
| Actionability ranking | `actionability_ranking.json` | `drug_name`, `gene_symbol`, `population_code`, `delta_vs_baseline`, `population_affected_pct`, `classification_strength` |

Transplant immunosuppressants in scope:

| Drug | Gene | CPIC Strength | Mechanism |
|---|---|---|---|
| tacrolimus | CYP3A5 | Strong | CYP3A5 extensive metabolizers clear tacrolimus faster — require higher doses to reach target trough |
| azathioprine | TPMT | Strong | TPMT poor metabolizers accumulate toxic thiopurine metabolites |
| azathioprine | NUDT15 | Strong | NUDT15*3 carriers at elevated myelosuppression risk independent of TPMT status |

## Stack (planned)

| Layer | Technology | Purpose |
|---|---|---|
| Ingestion | Python + boto3 | Pull Gold artifacts from pgx-latam-atlas S3 |
| Scoring | DuckDB | In-process SQL aggregation for TGI computation |
| Transformation | dbt Core | Reproducible, version-controlled TGI models |
| Storage | Apache Iceberg on S3 | Time-travel for index history across pipeline runs |
| Export | AWS Lambda | Commit JSON snapshots to portfolio repo |

## Methodology notes

1. **Baseline is CEU (Utah Residents, European ancestry, n=99).** This is the implicit reference
   population for CPIC dosing recommendations. TGI = 0 for CEU by construction.

2. **Deduplication.** When a drug-gene pair appears multiple times (e.g., different diplotype
   groups), only the first unique `drug_name|gene_symbol` per population is counted.

3. **Weighting.** CPIC classification strength is used as a proxy for clinical relevance.
   "Optional" recommendations are excluded from the index entirely.

4. **Populations included:** MXL (Mexican, n=64), PEL (Peruvian, n=85),
   CLM (Colombian, n=94), PUR (Puerto Rican, n=104).

## Limitations

- **Population-level signal only.** TGI reflects aggregate allele frequencies in research
  cohorts from the 1000 Genomes Project. It does not predict individual drug response.

- **Sample sizes are small.** N=64–104 per cohort introduces substantial uncertainty,
  especially for rare variants like NUDT15*3.

- **Not a clinical decision tool.** The index is designed to prioritize where
  pharmacogenomic testing programs would have the highest marginal benefit — it is not
  a substitute for validated genotyping and physician-guided dosing.

- **Gene scope is limited.** Only pharmacogenes with CPIC A/B evidence for transplant
  immunosuppressants are included. Other clinically relevant genes (e.g., ABCB1, CYP3A4)
  are not scored.
