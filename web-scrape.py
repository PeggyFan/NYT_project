import pandas as pd
import requests
import numpy as np
import time
import requests
import bs4
import json
from pymongo.errors import DuplicateKeyError, CollectionInvalid
from pymongo import MongoClient
import datetime as dt

client = MongoClient()
# Initiate Database
db = client['nyt_articles']
# Initiate Table
tab_biden = db['table_biden']
tab_biden.insert({'biden': 'cool'})

db_comments = client['nyt_comments']

tab_biden = db_comments['table_biden']
#db_comments.tab_biden.insert({'biden': 'cool'})

db = client['nyt_articles']
tab_carson = db['table_carson']
#tab_carson.insert({'carson': 'cool'})

db_comments = client['nyt_comments']
tab_carson = db_comments['table_carson']
#db_comments.tab_carson.insert({'carson': 'cool'})

NYT_URL = 'http://api.nytimes.com/svc/search/v2/articlesearch.json'
API_KEY = '74c73309c1052e6aa1785df7cd5cef8c:9:69947183'


# Query the NYT API once
def single_query(link, payload):
    response = requests.get(link, params=payload)
    if response.status_code != 200:
        print 'WARNING', response.status_code
    else:
        return response.json()

# Determine if the results are more than 100 pages
def more_than_100_pages(total_page):
    if total_page > 100:
        pages_left = min(total_page - 100, 100)
        return 100, pages_left, True
    else:
        return total_page, 0, False

# Looping through the pages give the number of pages
def loop_through_pages(total_pages, link, payload, table):
    for i in range(total_pages):
        if i % 50 == 0:
            print ' || Page ', i
        payload['page'] = str(i)
        content = single_query(link, payload)
        meta_lst = content['response']['docs']

        for meta in meta_lst:
            try:
                table.insert(meta)
            except DuplicateKeyError:
                print 'DUPS!'


# Scrape the meta data (link to article and put it into Mongo)
def scrape_meta(days=1, search_term, coll):

    # The basic parameters for the NYT API
    link = NYT_URL
    payload = {'api-key': API_KEY, 'q' : search_term, 'sort': 'newest'}

    today = dt.datetime(2015, 9, 22)
    yesterday = dt.datetime(2003, 9, 22)
    
    for day in range(days):
        payload['end_date'] = today.strftime("%Y%m%d")
        #yesterday = dt.date.today() - dt.timedelta(1)
        half_day = today - dt.timedelta(hours=12)
        payload['begin_date'] = yesterday.strftime("%Y%m%d")
        print payload
        print 'Scraping period: %s - %s ' % (str(yesterday), str(today))

        today -= dt.timedelta(days=2)
        
        content = single_query(link, payload)
        hits = content['response']['meta']['hits']
        total_pages = (hits / 10) + 1
        print 'HITS', hits

        newest_sort_pages, oldest_sort_pages, grt_100 = more_than_100_pages(total_pages)

        if grt_100:
            new_payload = payload.copy()
            old_payload = payload.copy()
            new_payload['sort']= 'newest'
            old_payload['sort'] = 'oldest'

        loop_through_pages(newest_sort_pages, link, new_payload, coll)
        loop_through_pages(oldest_sort_pages, link, old_payload, coll)

##Example
scrape_meta(days=1, 'Ben Carson', db.table_carson)

links = db.table_hilary.find({},{'web_url': 1, '_id' : 0})
links_h = []
for i in links:
    links_h.append(str(i['web_url']))
