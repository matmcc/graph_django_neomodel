import shelve
from bisect import bisect
from collections import Counter
import random

from graph_api.year_distribution import get_sample, percentiles_of_sample

# from neomodel import db, config
# config.DATABASE_URL = 'bolt://neo4j:password@localhost:7687'
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


with shelve.open('cached_function_calls', writeback=True) as db:
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
    # year = float(year) - unnecessary, python casts type for us
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
    coord = coord_percentile(year, percentile_dist_years, years_gt_one)
    return coord


def coord_rank(rank):
    """
    Return co-ordinate for rank based on percentile distribution of ranks in data
    e.g. if 66% of ranks are lte 24500, rank 24500 will return coord=66
    If one year covers several percentiles then that year will pick a random coord within that range
    """
    coord = coord_percentile(rank, percentile_dist_ranks)
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
