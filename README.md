# Amazon Spam Detection

A pipeline for classifying Amazon product reviews as spam ("Ham/Spam" style
labeling) using both classical NLP classifiers and neural-network (ANN)
approaches, with a Django REST backend and a small static front end for
interactive classification.

## Important Note
The dataset used to train the classifier and the ANN is from Kaggle,
found here: https://www.kaggle.com/datasets/dongrelaxman/amazon-reviews-dataset

## Status

This repository is an archived academic/experimental project. It is published
primarily for technical documentation and portfolio purposes and should not be
considered production-ready. `bin/util/DatabaseAdapter.py` and
`bin/util/Test.py` contain hardcoded PostgreSQL connection credentials
pointing at an external host; these must be removed/rotated before any public
use (see Known limitations).

## Overview

The project ingests Amazon review datasets (JSON, one file per product
category — e.g. CellPhonesAndAccessories, Electronics, HomeAndKitchen,
ClothingShoesAndJewelry, SportsAndOutdoors, ToysAndGames), stores them in a
PostgreSQL database, and trains classifiers to distinguish spam ("class 1")
from genuine ("class 0") reviews:

- **NLP path** (`bin/nlp`): builds a TF-IDF vocabulary/vectorizer and trains
  classical classifiers (e.g. Naive Bayes) on review text.
- **Non-NLP / ANN path** (`bin/nonnlp`): builds a Keras/TensorFlow ensemble
  ("AIO-ANN") using engineered features (review length, helpfulness counts,
  outputs of the NLP classifiers) rather than raw text; also includes a
  time-series preprocessing/analysis module.
- **Django backend** (`bin/django`): exposes the trained NLP classifiers and
  vectorizer through a REST API (`bin/django/api/backend`) for scoring new
  review text.
- **Front end** (`bin/website`): a static HTML/JS page (`index.html`,
  `app.js`) that submits review text to the Django API for classification.

## Features

- JSON dataset ingestion into PostgreSQL tables per product category
  (`bin/util/ParseJson.py`, `bin/util/DatabaseAdapter.py`).
- TF-IDF vectorization and vocabulary persistence for NLP classifiers
  (`bin/util/Vocabulator.py`, `bin/nlp`).
- Multiple NLP classifiers combined with an ANN ensemble on engineered
  features (`bin/nonnlp/ann`).
- Time-series preprocessing/analysis module (`bin/nonnlp/timeseries`).
- Django REST API serving pretrained models for review classification
  (`bin/django`).
- Static front end for manually submitting review text for classification
  (`bin/website`).
- `SQL.sql` with the raw PostgreSQL DDL/DML used to build and balance the
  training tables.
- Exploratory Jupyter notebooks per contributor under `notebooks/`.

## Structure

```text
bin/
  django/     Django project exposing pretrained classifiers via REST API
  nlp/        NLP classifier training/prediction (TF-IDF + classical models)
  nonnlp/     ANN ensemble + time-series analysis on engineered features
  non-nlp/    Additional time-series module (partial/legacy)
  util/       Shared config, PostgreSQL adapter, JSON parsing, vocabulary
  website/    Static front end (HTML/CSS/JS) calling the Django API
notebooks/    Exploratory Jupyter notebooks
SQL.sql       PostgreSQL DDL/DML for building and balancing training tables
requirements.txt  Python dependencies (TensorFlow/Keras, scikit-learn, Django, ...)
```

## Building and running

Unverified (as documented by the project, not independently executed in this
audit):

1. Configure `bin/util/DatabaseAdapter.py` to point at your own PostgreSQL
   instance (the checked-in credentials are placeholders left over from
   development and must not be reused).
2. Create the schema either via `Database.create_db()` in
   `DatabaseAdapter.py` or by running `SQL.sql` against the database.
3. Run `bin/nlp/nlp.py` to build the vocabulary/vectorizer and train the NLP
   classifiers. The classifier and vectorizer artifacts
   (`nlp-classifier-*.pkl`, `tfidf-vectorizer.pkl`) are written relative to
   the current working directory (`bin/nlp/classifiers/nlp_classifiers.py`),
   not to a dedicated `data/`/`trained/` directory; the JSON review datasets
   are loaded via `bin/util/ParseJson.py` and `bin/util/DatabaseAdapter.py`
   (PostgreSQL), and the `nonnlp` path reads them from `../../data/*.json`
   relative to `bin/nonnlp/nonnlp.py`.
4. Move the trained classifiers into
   `bin/django/api/backend/classifiers/` and the vectorizer into
   `bin/django/api/backend/vectorizer/`.
5. Start the Django server (`bin/django/api/manage.py runserver`, unverified)
   and serve the front end, e.g. `php -S 127.0.0.1:8000` from `bin/website`.
6. For the ANN ensemble, `full_aio_model_keras` in
   `bin/nonnlp/ann/net.py` (invoked from `bin/nonnlp/nonnlp.py`) trains the
   more complex "AIO-ANN" model; the project notes this requires a capable
   GPU/AI accelerator.

`pip install -r requirements.txt` (unverified in this audit) installs the
Python dependencies (TensorFlow/Keras, scikit-learn, pandas, psycopg2,
SQLAlchemy, Django, NLTK).

## Testing

No automated test suite was found beyond a placeholder
`bin/util/Test.py` and the default Django `tests.py`; no test command was
executed as part of this audit.

## Known limitations

- `bin/util/DatabaseAdapter.py` and `bin/util/Test.py` hardcode PostgreSQL
  host, credentials, and connect to a specific external IP address in
  multiple functions; this is a publication blocker and must be remediated
  (rotate/remove credentials, parameterize via environment variables) before
  making the repository public.
- `bin/django/api/api/settings.py` contains a hardcoded Django `SECRET_KEY`
  (the framework-generated `django-insecure-...` development default); it
  should be replaced with a value sourced from the environment before any
  non-local deployment.
- The project's own documentation states the ANN ensemble ("AIO-ANN") works
  but offers no real benefit over the classical NLP classifiers for
  real-world use.
- Trained model artifacts (`.pkl`, `.rar`) and the Django `db.sqlite3` file
  are present in the working tree; they are large/generated and are excluded
  via `.gitignore` rather than tracked. This repository has not yet been
  initialized under version control, so no history-level secret removal is
  currently required, but these files must remain untracked once it is.
- A front-end `node_modules/` directory is present under `bin/website/`; it
  is a dependency directory and is excluded via `.gitignore`. The
  corresponding `package.json`/`package-lock.json` (declaring only a
  `bootstrap` dependency) live under `bin/website/dataFiles/` rather than
  `bin/website/`, which is inconsistent with typical npm project layout.
- `bin/website/KI_UEB1_2.pdf` is a bundled document of unverified origin and
  redistribution rights (its name suggests a university course assignment
  sheet); verify its provenance before publishing the repository.

Any copying, modification, redistribution, incorporation into other software, or commercial use requires prior written permission. Requests are expressly welcome and will generally be approved; commercial use may be subject to an agreed licence fee or revenue-sharing arrangement.

Copyright © 2026 Philip Weber. All rights reserved.

