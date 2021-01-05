# TREC News Index

This repository contains Docker and Python files to index the TREC Washington Post News corpus with Elasticsearch.

## Source data

The Washington Post corpus is 7GB so it is not on Github. The paths used assume the zip file provided to TREC participants is extracted to the `wapo/` directory. The only file from the zip that is required is `wapo/data
TREC_Washington_Post_collection.v3.jl`.

## Python dependencies

This project is written Python3 and has some dependencies.

```
python3 -m venv venv
source venv/bin/active
pip install -r requirements.txt
```

## Elasticsearch

This requires Docker. It also includes Kibana for convienence. 

```
docker-compose up
```

Both services are available on the default ports.

* Elasticsearch - [localhost:9200](http://localhost:9200)
* Kibana - [localhost:5601](http://localhost:5601)


To index:

```
python es-ingest.py
```

The schema is defined in `schema.json`.

Index problems:

Currently all articles are indexed successfully with version 3 of the corpus. But that could change with new versions.

Any articles that have problems being indexed, will be written out to `es-output.jsonl`. The notebook `problems-ingesting.ipynb` is for interactive debugging of these problems.

