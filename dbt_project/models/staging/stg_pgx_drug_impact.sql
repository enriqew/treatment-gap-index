{{ config(materialized='view') }}

SELECT
    drug_name,
    gene_symbol,
    population_code,
    CAST(delta_vs_baseline AS DOUBLE)          AS delta_vs_baseline,
    CAST(percentage_requiring_change AS DOUBLE) AS percentage_requiring_change,
    CAST(baseline_ceu_percentage AS DOUBLE)     AS baseline_ceu_percentage,
    classification_strength
FROM read_json_auto(
    '{{ env_var("TGI_RAW_PATH", "../data/raw") }}/pgx_artifacts/*/drug_impact_summary.json'
)
WHERE drug_name IS NOT NULL
  AND gene_symbol IS NOT NULL
  AND population_code IS NOT NULL
