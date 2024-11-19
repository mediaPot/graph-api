get_nodes = "MATCH (n) RETURN n LIMIT 5"
get_labels_and_counts = "MATCH (n) RETURN DISTINCT labels(n), count(*)"


def get_subset(label, keyword: str):
    return f"match (n:{label} {{name: '{keyword}'}}) -[r] -(m) return n, r, m"


def get_subset_stemmed(label, keyword: str):
    return f"MATCH (n:{label})-[r]-(m) WHERE '{keyword}' IN n.location_ref RETURN n, r, m"
