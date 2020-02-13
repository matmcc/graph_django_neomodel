import os
import shelve
from bisect import bisect
from collections import Counter
import random
from datetime import datetime

from graph_api.db.year_distribution import get_sample, percentiles_of_sample, get_sample_lt

# from neomodel import db, config
# config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'
from graph_django_neomodel.settings import BASE_DIR

SAMPLE_SIZE = 100000


# functions to cache
def percentile_distribution_of_sample(node_type, node_property, sample_size):
    sample = get_sample(node_type, node_property, sample_size)
    distribution = percentiles_of_sample(sample)
    return distribution


def count_gt_sentinel(sequence, sentinel):
    values_gt_sentinel = Counter(sequence)
    values_gt_sentinel = {v: count_v for v, count_v in values_gt_sentinel.items() if count_v > sentinel}
    return values_gt_sentinel


def percentile_distribution_of_sample_lt(node_type, node_property, sample_size, limit):
    sample = get_sample_lt(node_type, node_property, sample_size, limit)
    distribution = percentiles_of_sample(sample)
    return distribution


def build_distribution_dict(distribution_dict, min_v, max_v):
    """Builds a dictionary of values {query_value: percentile distribution of value in sampled MAG data}"""
    keys = sorted(distribution_dict.keys())    # sorted list of percentile values (i.e. 1 - 100)
    min_val = min_v
    max_val = max_v + 1
    return_dict = {}
    # check for items where the value covers more than one percentile:
    dist_gt_one = count_gt_sentinel(distribution_dict.values(), 1)
    # create keys for values from min - first key
    for val in range(min_val, distribution_dict[keys[0]]):
        return_dict[val] = [keys[0]]
    # create values for  non-end percentiles
    for key in keys[1:-1]:  # skip first and last value
        if distribution_dict[key] in dist_gt_one:   # value covers more than one percentile
            val = distribution_dict[key]
            lower = key - 1 if dist_gt_one[val] == 2 else key - 2
            upper = key - 2 + dist_gt_one[val]
            return_dict[val] = [lower, upper]
        else:  # value accounts for 1 pc - build up year dict
            for val in range(distribution_dict[key], distribution_dict[key + 1]):
                return_dict[val] = [key]   # store as list so we can compare lengths when year covers >1 pc
    # create keys for values beyond last (or last but two or but one) value
    if distribution_dict[keys[-1]] in dist_gt_one:  # last key accounts for more than 1 percentile
        for val in range(distribution_dict[keys[-1]] + 1, max_val):
            return_dict[val] = [keys[-1]]
    elif distribution_dict[keys[-2]] in dist_gt_one:    # last but one key accounts for more than one percentile
        for val in range(distribution_dict[keys[-2]] + 1, max_val):
            return_dict[val] = [keys[-1]]
    else:
        for val in range(distribution_dict[keys[-1]], max_val):
            return_dict[val] = [keys[-1]]
    # in case logic has missed keys, add them matching lower neighbour.
    for i in range(min_val, max_val):
        if i not in return_dict:
            return_dict[i] = return_dict[i - 1]
    return return_dict


with shelve.open(os.path.join(BASE_DIR, 'mag', 'cached_function_calls'), writeback=True) as db:
    if 'percentile_distribution_years' in db:
        percentile_dist_years = db['percentile_distribution_years']
    else:
        percentile_dist_years = percentile_distribution_of_sample('Paper', 'Year', SAMPLE_SIZE)
        db['percentile_distribution_years'] = percentile_dist_years
    if 'years_gt_one' in db:
        years_gt_one = db['years_gt_one']
    else:
        years_gt_one = count_gt_sentinel(percentile_dist_years.values(), 1)
        db['years_gt_one'] = years_gt_one
    if 'percentile_dist_ranks' in db:
        percentile_dist_ranks = db['percentile_dist_ranks']
    else:
        percentile_dist_ranks = percentile_distribution_of_sample('Paper', 'Rank', SAMPLE_SIZE)
        db['percentile_dist_ranks'] = percentile_dist_ranks
    if 'year_distribution' in db:
        year_distribution = db['year_distribution']
    else:
        year_distribution = build_distribution_dict(percentile_dist_years, 1850, datetime.now().year)
        db['year_distribution'] = year_distribution
    if 'rank_distribution' in db:
        rank_distribution = db['rank_distribution']
    else:
        rank_distribution = build_distribution_dict(percentile_dist_ranks, 10000, 50000)
        db['rank_distribution'] = rank_distribution
    if 'percentile_distribution_citations' in db:
        percentile_distribution_citations = db['percentile_distribution_citations']
    else:
        percentile_distribution_citations = percentile_distribution_of_sample('Paper', 'CitationCount', SAMPLE_SIZE)
        db['percentile_distribution_citations'] = percentile_distribution_citations
    if 'citation_distribution' in db:
        citation_distribution = db['citation_distribution']
    else:
        citation_distribution = build_distribution_dict(percentile_distribution_citations, 0, 250000)
        db['citation_distribution'] = citation_distribution

# This was slow, because of repeated list iteration - so built a year dict
def coord_percentile(value, distribution, dist_gt_one=None):
    """
    Return co-ordinate for value based on percentile distribution of values
    e.g. with value=year, if 66% of years are lte 1980, year 1980 will return coord=66
    If one year covers several percentiles then that year will pick a random coord within that range
    if this has already been calculated it can be passed as dist_gt_one
    value: item to compare to list, e.g. int
    distribution: dict {percentile: value}
    """
    values = list(distribution.values())
    # todo: fix hardcoded hack for most recent years?
    coord = 0
    if not dist_gt_one:
        dist_gt_one = count_gt_sentinel(distribution.values(), 1)
    if value in dist_gt_one:
        # pick co-ord in range
        coord = random.randrange(values.index(value) + 1, values.index(value) + 1 + dist_gt_one[value])
    else:
        top_val = values[-1]
        if value <= top_val:
            coord = bisect(values, value)
        else:
            # value > biggest value in values, so add difference to 99
            # this may give co-ord > 100, but sigma.js will scale co-rds to best fit available space
            coord = 99 + value - top_val
    return int(coord)


def coord_year(year):
    """
    Return co-ordinate for year based on percentile distribution of years in data
    e.g. if 66% of years are lte 1980, year 1980 will return coord=66
    If one year covers several percentiles then that year will pick a random coord within that range
    """
    coord = year_distribution[year]
    if len(coord) > 1:
        coord = random.randint(coord[0], coord[1])
    else:
        coord = coord[0]
    return coord


def coord_rank(rank):
    """
    Return co-ordinate for rank based on percentile distribution of ranks in data
    e.g. if 66% of ranks are lte 24500, rank 24500 will return coord=66
    If one year covers several percentiles then that year will pick a random coord within that range
    """
    rank_min = 10000
    rank_max = 50000
    if not rank:
        print("rank is null")
        return random.randrange(0, 101)
    if rank < rank_min:
        return 101
    if rank > rank_max:
        return 0
    try:
        coord = rank_distribution[rank]
    except KeyError as err:
        print(err, rank)
        return random.randrange(0, 101)
    if len(coord) > 1:
        coord = random.randint(coord[0], coord[1])
    else:
        coord = coord[0]
    # rank would need reversing, as lower => more important
    # but y co-ord's are drawn 0-100 from top-bottom
    # and we more important papers to be at the top
    # so we can leave as is
    # if reversing is needed, uncomment next line
    # coord = 101 - coord
    return coord


def coord_citation(value):
    coord = citation_distribution[value]
    if len(coord) > 1:
        coord = random.randint(coord[0], coord[1])
    else:
        coord = coord[0]
    # value needs reversing for y-axes due to sigma y-coord handling
    coord = 101 - coord
    return coord

def coord_year_old(year):
    """
    Return co-ordinate for year based on percentile distribution of years in data
    e.g. if 66% of years are lte 1980, year 1980 will return coord=66
    If one year covers several percentiles then that year will pick a random coord within that range
    """
    coord = coord_percentile(year, percentile_dist_years, years_gt_one)
    return coord


def coord_rank_old(rank):
    """
    Return co-ordinate for rank based on percentile distribution of ranks in data
    e.g. if 66% of ranks are lte 24500, rank 24500 will return coord=66
    If one year covers several percentiles then that year will pick a random coord within that range
    """
    coord = coord_percentile(rank, percentile_dist_ranks)
    print(rank, coord)
    # rank would need reversing, as lower => more important
    # but y co-ord's are drawn 0-100 from top-bottom
    # and we more important papers to be at the top
    # so we can leave as is
    # if reversing is needed, uncomment next line
    # coord = 101 - coord
    return coord


def coord_random(range_min=0, range_max=100):
    return random.randrange(range_min, range_max)


def get_max_louvain():
    # Todo: temp hardcoded value / build setup louvain at start?
    return 42  # db.cypher_query("match (p:Paper) return max(p.community)")[0][0][0]


community_max = get_max_louvain()


def coord_community(comm):
    mult = 100 / (community_max + 1)
    co_ord = (comm + 1) * mult
    # add a little random variation so that items are less likely to share a co_ord
    co_ord += random.uniform(-0.5, 0.5)
    return co_ord
