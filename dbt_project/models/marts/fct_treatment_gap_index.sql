{{ config(materialized='table') }}

WITH drug_entries AS (
    SELECT
        population_code,
        drug_name,
        gene_symbol,
        delta_vs_baseline,
        classification_strength,
        CASE classification_strength
            WHEN 'Strong'   THEN 1.0
            WHEN 'Moderate' THEN 0.7
            WHEN 'Optional' THEN 0.4
            ELSE 0.5
        END AS strength_weight,
        ROW_NUMBER() OVER (
            PARTITION BY population_code, drug_name, gene_symbol
            ORDER BY ABS(delta_vs_baseline) DESC
        ) AS rn
    FROM {{ ref('stg_pgx_drug_impact') }}
    WHERE drug_name IN ('tacrolimus', 'azathioprine')
      AND population_code != 'CEU'
),
deduped AS (
    SELECT * FROM drug_entries WHERE rn = 1
)
SELECT
    population_code,
    ROUND(
        SUM(ABS(delta_vs_baseline) * strength_weight) / NULLIF(SUM(strength_weight), 0),
        2
    ) AS treatment_gap_index,
    COUNT(*) AS n_drug_gene_pairs,
    -- Breakdown columns
    MAX(CASE WHEN drug_name = 'tacrolimus' AND gene_symbol = 'CYP3A5' THEN ABS(delta_vs_baseline) END) AS tacrolimus_cyp3a5_delta,
    MAX(CASE WHEN drug_name = 'azathioprine' AND gene_symbol = 'TPMT'   THEN ABS(delta_vs_baseline) END) AS azathioprine_tpmt_delta,
    MAX(CASE WHEN drug_name = 'azathioprine' AND gene_symbol = 'NUDT15' THEN ABS(delta_vs_baseline) END) AS azathioprine_nudt15_delta
FROM deduped
GROUP BY population_code
ORDER BY treatment_gap_index DESC
