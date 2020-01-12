from collections import Counter
import random
from neomodel import db


def get_year_percentile(percentile):
    return db.cypher_query("match (p:Paper) return percentiledisc(p.year, {pc})", {'pc': percentile})[0][0][0]


# Build dict of percentile:year boundary for papers in db
dict_of_percentiles = {pc:get_year_percentile(pc/100) for pc in range(1, 100)}

# build dict of years which span more than 1pc - year:count of years
years_gt_one = Counter(dict_of_percentiles.values())
years_gt_one = {year: count_years for year, count_years in years_gt_one.items() if count_years > 1}


def coord_year(year):
    years = list(dict_of_percentiles.values())
    # todo: fix hardcoded hack for year == 2020
    if year >= 2020:
        return 100
    if year in years_gt_one:
        return random.randrange(years.index(year) + 1, years.index(year) + 1 + years_gt_one[year])
    else:
        for y in years:
            if year <= y:
                return years.index(y) + 1




def get_max_louvain():
    return db.cypher_query("match (p:Paper) return max(p.community)")[0][0][0]


community_max = get_max_louvain()


def coord_community(comm):
    mult = 100 / (community_max + 1)
    co_ord = (comm + 1) * mult
    # add a little random variation so that items are less likely to share a co_ord
    co_ord += random.uniform(-0.5, 0.5)
    return co_ord
