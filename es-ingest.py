# coding: utf-8
import json
import requests
import jsonlines
import re
import pickle
import time

from elasticsearch import Elasticsearch, helpers
from tqdm import tqdm

batch_size = 5000
es = Elasticsearch()
index = 'wapo'
schema = json.load(open('schema.json'))

es.indices.delete(index = index, ignore = 404)
es.indices.create(index = index, body = schema)

archive_path = 'wapo/data/TREC_Washington_Post_collection.v3.jl'

def index_docs(docs):
    helpers.bulk(es, articles, index = 'wapo', request_timeout = 100)
    docs.clear()

# Process data
print('Processing data...')

articles = []
problems = []
idx = 0
with jsonlines.open(archive_path) as reader:
    for x in tqdm(reader):

        try:
            doc_id = x["id"]

            # some parts are nested in the top-level 'contents'
            contents = [y for y in x["contents"] if y is not None]

            def extractor(value):
                try:
                    idx = [x['type'] for x in contents].index(value)
                    ret = contents[idx]['content']
                except:
                    ret = None
                return ret

            kicker = extractor('kicker')

            if (kicker in ["Opinion", "Letters to the Editor", "The Post's View"]):
                continue
            if (x["author"] in ["AP", "Associated Press", "Reuters"] or bool(re.search("^Associate", x["author"]))):
                continue

            date = extractor('date')
            
            # the content is weirder 
            para_idx = [i for i, x in enumerate(contents) if ('subtype' in x) and x['subtype'] == "paragraph"]
            contents_all = ''.join([contents[i]['content'] for i in para_idx])
            links = re.findall('<a href="(.*?)".*?>', contents_all)

            def strip_html(data):
                p = re.compile(r'<.*?>')
                return p.sub('', data)

            def strip_loc(string):
                string = re.sub("^.* — ?", "", str(string))
                return string

            def none_if_short_contents(idx):
                try:
                    i = para_idx[idx]
                    ret = strip_html(contents[i]['content'])
                except:
                    ret = None
                return ret

            article = {
                "_id": doc_id,
                "title": x["title"],
                "author": x["author"],
                "date": date,
                "kicker": kicker,
                "contents_1": strip_loc(none_if_short_contents(0)),
                'contents_2': none_if_short_contents(1),
                'contents_3': none_if_short_contents(2),
                'contents_all': strip_html(contents_all),
                'links': links
            }
            articles.append(article)

        except (EOFError, IndexError, TypeError, ValueError, KeyError) as e:
            problems.append(x)

        idx += 1

        if len(articles) >= batch_size:
            index_docs(articles)

# One last push
index_docs(articles)

with jsonlines.open('es-output.jsonl', 'w') as writer:
    writer.write_all(problems)

print(f"{str(round(100 * (len(problems) / idx), 2))}% of docs had ingestion errors")
