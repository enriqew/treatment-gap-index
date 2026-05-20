.PHONY: install ingest build test export all clean

install:
	pip install -e ".[dev]"

ingest:
	python -m ingest.pgx_artifacts

build:
	cd dbt_project && dbt deps && dbt run

test:
	cd dbt_project && dbt test
	pytest tests/

export:
	python -m src.treatment_gap.export

all: ingest build test export

clean:
	rm -rf data/raw data/exports/[!.]*
