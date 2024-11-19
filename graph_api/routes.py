from collections import Counter
from datetime import datetime

from fastapi import APIRouter, Depends

from graph_api import logger
from graph_api.db_connector import Neo4jConnector

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
        robject["connected_node_name"] = r["connected_node"]._properties["name"]

        if labels[0] == "Title":
            robject["connected_node_url"] = r["connected_node"]._properties["url"]
            robject["connected_node_date"] = r["connected_node"]._properties["date"]
            robject["connected_node_sentiment"] = r["connected_node"]._properties["sentiment"]
            robject["connected_node_provider"] = r["connected_node"]._properties["provider"]
            robject["datetime"] = robject["connected_node_date"]  # r["relationship"]._properties["date"]
            parts = robject["datetime"].split("T")
            robject["date"] = parts[0]
            robject["time"] = parts[1].split(".")[0]
        else:
            key = [i for i in list(r["connected_node"]._properties.keys()) if i.endswith('_ref')][0]
            robject[f"connected_node_{key}"] = r["connected_node"]._properties[key][0]

        robject["relationship_type"] = r["relationship"].type
        robject["relationship_element_id"] = r["relationship"].element_id
        results.append(robject)

    locations, orgs, persons = [], [], []
    if label == "Title":

        locations = [
            i["connected_node_location_ref"]
            for i in results
            if i["connected_node_label"] == "Location"
        ]
        orgs = [
            i["connected_node_org_ref"]
            for i in results
            if i["connected_node_label"] == "Org"
        ]
        persons = [
            i["connected_node_person_ref"]
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
