from neomodel import db
import numpy as np


# acting weird and I don't know why - hardcoded version below
def get_sample(node_type, node_property, sample_size):
    q = f"MATCH (n:{node_type}) WHERE rand() < 0.1 WITH n LIMIT {sample_size} RETURN n.{node_property}"
    results, meta = db.cypher_query(q)
    return results


# def get_sample(sample_size):
#     q = "MATCH (n:Paper) WHERE rand() < 0.1 WITH n LIMIT {sample_size} RETURN n.Year"
#     results, meta = db.cypher_query(q, {"sample_size": sample_size})
#     return results


def percentiles_of_sample(sample):
    a = np.array(sample)
    percentiles = {i: np.percentile(a, i) for i in range(1, 101)}
    return percentiles
