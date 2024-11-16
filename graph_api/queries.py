get_nodes = "MATCH (n) RETURN n LIMIT 5"
get_labels_and_counts = "MATCH (n) RETURN DISTINCT labels(n), count(*)"


def get_subset_stemmed(label, keyword: str):
    # return f"match (n:{label} {{name: '{keyword}'}}) -[r] -(m) return n, r, m"
    # print(label, keyword)
    return f"MATCH (n:{label})-[r]-(m) WHERE '{keyword}' IN n.location_ref RETURN n, r, m"

def get_subset(label, keyword: str):
    return f"match (n:{label} {{name: '{keyword}'}}) -[r] -(m) return n, r, m"


def get_articles_by_language(lang: str):
    query = ""
    if lang == "gr":
        query = "match (n: Title) where n.name =~ '.*[\u0370-\u03FF].*' or (n.name =~ '.*[A-Za-z].*' AND n.name =~ '.*[\u0370-\u03FF].*') return n order by n.date"
    elif lang == "en":
        query = "match (n: Title) where n.name =~ '.*[A-Za-z].*' and not n.name =~ '.*[\u0370-\u03FF].*' return n order by n.date"
    else:
        raise NotImplementedError("No supported language.")

    return query
