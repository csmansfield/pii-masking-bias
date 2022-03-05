# Behind the Mask: Demographic bias in PII masking

This repository provides data links, data sampling notebooks, a codebase for running PII maskers, and analysis notebooks for the paper "Behind the Mask: Demographic bias in PII masking".

## Setup:

``pip install -r requirements.txt``

## Sampling datasets:

You can get links to download datasets and sample names with ``data/sample_LAR.ipynb`` and ``data/sample_NY.ipynb`` for LAR and NYC name lists.  The Congress dataset (which was labeled manually) is found at ``data/congress.csv``.

Run ``python data/slot_filler.py name_list_directory output_directory templates.csv`` to generate full datasets.

## Running PII maskers:

Presidio requires the spaCy en transformers model: ``python -m spacy download en_core_web_trf``

AWS and GCP require proper credentials. AWS credentials are stored as environment variables ``aws_access_key_id`` and ``aws_secret_access_key``, while ``GOOGLE_APPLICATION_CREDENTIALS`` should reference your ``google_keyfile.json`` file.  

A script for running experiments across all systems can be run with ``python pii_benchmarking/run_experiments.py``.

If there are issues with loading package-internal imports, install the package in develop mode from the local path with ``pip install -e pii-benchmarking``.

## Analysis:

Analysis notebooks and figures are found in ``analysis``.
