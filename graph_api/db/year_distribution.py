from neomodel import db
import numpy as np


def get_sample(node_type, node_property, sample_size):
    q = f"MATCH (n:{node_type}) WHERE rand() < 0.33 WITH n LIMIT {sample_size} RETURN n.{node_property}"
    results, meta = db.cypher_query(q)
    return results


def get_sample_gt(node_type, node_property, sample_size, gt):
    q = f"MATCH (n:{node_type}) WHERE rand() < 0.33 AND n.{node_property} > {gt} WITH n LIMIT {sample_size} RETURN n.{node_property}"
    results, meta = db.cypher_query(q)
    return results


def get_sample_lt(node_type, node_property, sample_size, lt_limit):
    q = f"MATCH (n:{node_type}) WHERE rand() < 0.33 AND n.{node_property} < {lt_limit} WITH n LIMIT {sample_size} RETURN n.{node_property}"
    results, meta = db.cypher_query(q)
    return results


def percentiles_of_sample(sample):
    a = np.array(sample)
    percentiles = {i: int(np.percentile(a, i).item()) for i in range(1, 101)}   # cast from np_float64 to python int
    return percentiles
