import os
import string
import heapq
import json

from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from graph_api import logger
from graph_api.db_connector import Neo4jConnector

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

router = APIRouter(prefix="/graph", tags=["graph-api"])
neo4j = Neo4jConnector()


@router.get("/welcome/")
def welcome():
    logger.info("Get request @ /graph/welcome")
    return {"message": "Graph API "}


@router.get("/nodes/")
async def get_nodes(session=Depends(neo4j.get_neo4j_session)):
    result = session.run(neo4j.queries.get_nodes)
    nodes = [record["n"] for record in result]
    return {"nodes": nodes}


@router.get("/labels-and-counts/")
async def get_labels_and_counts(session=Depends(neo4j.get_neo4j_session)):
    result = session.run(neo4j.queries.get_labels_and_counts)
    lnc = [{"label": record[0][0], "count": record[1]} for record in result]

    return {"labels_and_counts": lnc}


@router.get("/articles-subset/{lang}")
async def get_articles_subset(lang: str, session=Depends(neo4j.get_neo4j_session)):
    result = session.run(neo4j.queries.get_articles_by_language(lang))
    with open("new_tweets_dataset/mediapot_el_tweets.json", "r") as d:
        tweets = json.load(d)
    gs = [
        {
            "node": record["n"]
        }
        for record in result
    ]
    results = []
    titles = []
    cleaned_titles = []
    sentiments = []
    dates = []
    providers = []
    urls = []
    with open("graph_api/stopwords.txt", "r") as f:
        sw = f.read().splitlines()

    data_per_date = {"articles": {}, "tweets": {}}
    for g in gs:
        cleaned_titles.append(' '.join([word.rstrip(string.punctuation).lower() for word in g['node']._properties['name'].split() if word.lower() not in sw]))
        titles.append(g['node']._properties['name'])
        sentiments.append(g['node']._properties['sentiment'])
        dates.append(g['node']._properties['date_day'])
        providers.append(g['node']._properties['provider'])
        urls.append(g['node']._properties['url'])

        results.append(g['node']._properties)

        if g['node']._properties['date_day'] not in data_per_date["articles"].keys():
            data_per_date["articles"][g['node']._properties['date_day']] = [word.rstrip(string.punctuation).lower() for word in g['node']._properties['name'].split() if word.lower() not in sw]
        else:
            data_per_date["articles"][g['node']._properties['date_day']].extend([word.rstrip(string.punctuation).lower() for word in g['node']._properties['name'].split() if word.lower() not in sw])

    articles_per_date = Counter(dates)
    ud = [k for k, v in articles_per_date.items()]
    freq = [v for k, v in articles_per_date.items()]
    filtered_tweets = []
    tweet_dates = []
    tweet_text = []
    for tweet in tweets["response"]["docs"]:
        if tweet["created_date"].split("T")[0] in ud:
            filtered_tweets.append(tweet)
            tweet_dates.append(tweet["created_date"].split("T")[0])
            tweet_text.append(' '.join([word.rstrip(string.punctuation).lower() for word in tweet['text']]))
        if tweet["created_date"].split("T")[0] not in data_per_date["tweets"].keys():
            data_per_date["tweets"][tweet["created_date"].split("T")[0]] = [word.lower() for word in tweet['text'].split() if word not in sw]
        else:
            data_per_date["tweets"][tweet["created_date"].split("T")[0]].extend([word.lower() for word in tweet['text'].split() if word not in sw])

    tweets_per_date = Counter(tweet_dates)
    top_words_per_date = {"articles": {}, "tweets": {}}

    for u in ud:
        if u not in tweets_per_date.keys():
            tweets_per_date[u] = 0
            top_words_per_date["tweets"][u] = []
        else:
            twordcloud = WordCloud().generate(' '.join(data_per_date["tweets"][u]))
            word_freq = twordcloud.words_
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            top_words_per_date["tweets"][u] = top_words

        awordcloud = WordCloud().generate(' '.join(data_per_date["articles"][u]))
        word_freq = awordcloud.words_
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        top_words_per_date["articles"][u] = top_words


    freq_tweets = [tweets_per_date[u] for u in ud]

    print(top_words_per_date)
    time_series = pd.DataFrame({
    'freq': freq,
    'freq_tweets': freq_tweets
    }, index=ud)
    plt.figure(figsize=(20, 12))  # Set the figure size
    plt.plot(time_series.index, time_series['freq'], marker='o', linestyle='-', color='b', label='Frequency')
    plt.plot(time_series.index, time_series['freq_tweets'], marker='x', linestyle='--', color='r', label='Frequency of Tweets')
    plt.margins(y=0.2)
    plt.autoscale(enable=True, axis='y')
    for i in range(len(time_series)):
        # plt.text(time_series.index[i], time_series['freq'].iloc[i] + 0.5, str(time_series['freq'].iloc[i]),
        #          fontsize=12, color='blue', ha='center')  # Annotate freq points
        plt.text(time_series.index[i], time_series['freq_tweets'].iloc[i] + 0.5, str(time_series['freq_tweets'].iloc[i]),
                 fontsize=12, color='red', ha='center')  # Annotate freq_tweets points
        plt.text(time_series.index[i], time_series['freq'].iloc[i] - i* 500, str('\n'.join([k[0] for k in top_words_per_date["articles"][time_series.index[i]]])),
                 fontsize=12, color='blue', ha='center')
        plt.text(time_series.index[i], time_series['freq_tweets'].iloc[i] - i * 1000, str(','.join([k[0] for k in top_words_per_date["tweets"][time_series.index[i]]])),
                 fontsize=12, color='red', ha='center')
        # for i, (date, top_words) in enumerate(zip(ud, top5words)):
    #     # Format the top words as a string (first three words)
    #     annotation = ', '.join([word for word, freq in top_words[:5]])
    #     # Annotate the point on the plot
    #     plt.annotate(annotation, (date, freq[i]), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

    plt.savefig(os.path.join("timeseries.png"), dpi=300)  # Save the figure with 300 DPI for high resolution

    # return {"total_articles": len(results), "articles_per_date": articles_per_date}
    return FileResponse("timeseries.png")
def get_date(d):
    date_value = ""
    try:
        date_value = datetime.strptime(d["datetime"], "%Y-%m-%dT%H:%M:%S.%f%z")
    except Exception:
        date_value = datetime.strptime(d["datetime"], "%Y-%m-%dT%H:%M:%S%z")
    return date_value


@router.get("/graph-subset/{label}/{keyword}")
async def graph_subset(
    label: str, keyword: str, session=Depends(neo4j.get_neo4j_session)
):
    if label == "Title":
        result = session.run(neo4j.queries.get_subset(label, keyword))
    else:
        result = session.run(neo4j.queries.get_subset_stemmed(label, keyword))
    gs = [
        {
            "node": record["n"],
            "relationship": record["r"],
            "connected_node": record["m"],
        }
        for record in result
    ]
    results = []

    connected_node_labels = []
    for j in range(0, len(gs)):
        connected_node_labels.append([i for i in gs[j]["connected_node"].labels][0])

    connected_node_labels_set = Counter(connected_node_labels)
    if len(gs) > 0:
        connected_node_labels_set["element_id"] = gs[0]["node"].element_id

    for i, r in enumerate(gs):
        robject = {}
        node_labels = [i for i in gs[0]["node"].labels]
        robject["label"] = node_labels[0]
        robject["name"] = r["node"]._properties["name"]
        robject["element_id"] = r["node"].element_id
        labels = [i for i in gs[i]["connected_node"].labels]
        robject["connected_node_element_id"] = r["connected_node"].element_id
        robject["connected_node_label"] = labels[0]
        if labels[0] == "Title":
            robject["connected_node_name_ref"] = r["connected_node"]._properties[f'{list(r["connected_node"].labels)[0].lower()}_ref'][0]
            robject["connected_node_url"] = r["connected_node"]._properties["url"]
            robject["connected_node_date"] = r["connected_node"]._properties["date"]
            robject["connected_node_sentiment"] = r["connected_node"]._properties["sentiment"]
            robject["connected_node_provider"] = r["connected_node"]._properties["provider"]
            robject["datetime"] = robject["connected_node_date"]  # r["relationship"]._properties["date"]
            parts = robject["datetime"].split("T")
            robject["date"] = parts[0]
            robject["time"] = parts[1].split(".")[0]

        robject["relationship_type"] = r["relationship"].type
        robject["relationship_element_id"] = r["relationship"].element_id
        results.append(robject)

    locations, orgs, persons = [], [], []
    if label == "Title":
        locations = [
            i["connected_node_name_ref"]
            for i in results
            if i["connected_node_label"] == "Location"
        ]
        orgs = [
            i["connected_node_name_ref"]
            for i in results
            if i["connected_node_label"] == "Org"
        ]
        persons = [
            i["connected_node_name_ref"]
            for i in results
            if i["connected_node_label"] == "Person"
        ]
        locations.sort()
        orgs.sort()
        persons.sort()
    else:
        sorted_results = sorted(results, key=get_date, reverse=True)
        oldest = sorted_results[0]["date"] if len(sorted_results) > 0 else ""
        newest = sorted_results[-1]["date"] if len(sorted_results) > 0 else ""

    connected_node_labels_set["locations"] = locations
    connected_node_labels_set["orgs"] = orgs
    connected_node_labels_set["persons"] = persons

    if label == "Title":
        re = {
            "connected_node_labels": connected_node_labels_set,
            "graph_subset": results,
            "length": len(results),
        }
    else:
        re = {
            "connected_node_labels": connected_node_labels_set,
            "graph_subset": sorted_results,
            "length": len(sorted_results),
            "oldest": oldest,
            "newest": newest,
        }


    return re
