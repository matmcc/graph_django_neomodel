import requests
from requests.exceptions import HTTPError
from urllib.parse import urljoin
from functools import lru_cache
from timeit import default_timer as timer
from time import sleep

# ### Mag_Api class
# This class contains functions to call the MAG API.
# Docs here:
# https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/queryexpressionsyntax


class Mag_Api:

    def __init__(self):
        # ## Properties
        # Set session params
        # BaseUrlSession sets a base URL
        self.API_KEY = 'c18d1cd543c540048f8f9eba07cde079'
        self.MAG_BASE_URL = 'https://api.labs.cognitive.microsoft.com/academic/v1.0/'

        # default attributes to fetch
        self.ATTRIBS = "Id,Ti,DN,Y,CC,AA.AuN,AA.DAuN,AA.AuId,RId,F.FN,F.DFN,F.FId,DOI,S,IA"  # F.Fn,E.DOI
        # Id: int - UID
        # Ti: str - Title of paper - normalized
        # DN: str - Title, display name
        # Y: int - Year
        # CC: int - Number of citations
        # AA.AuN: 'AA': ['AA.AuN': Name1, ...] - list of author names
        # AA.DAuN: as above - author display name
        # AA.AuId: int - Author Id
        # RId: list of ints - list of referenced papers, by Id
        # F.FN: str - field of study, normalized
        # F.DFN: str - field of study, display name
        # F.FId: int - FoS, Id
        # DOI: str - DOI
        # IA: inverted abstract
        # S: source URLs

        # timer flags
        self.start = None
        self.elapsed = None

        # inner class setting base URL for requests
        class BaseUrlSession(requests.Session):

            def __init__(self, prefix_url=None, *args, **kwargs):
                super(self.__class__, self).__init__(*args, **kwargs)
                self.prefix_url = prefix_url

            def request(self, method, url, *args, **kwargs):
                url = urljoin(self.prefix_url, url)
                return super(self.__class__, self).request(method, url, *args, **kwargs)

        # set up session
        self.session = BaseUrlSession(self.MAG_BASE_URL)
        self.session.headers.update({'Ocp-Apim-Subscription-Key': self.API_KEY})

    # ### API methods
    @lru_cache(maxsize=32)
    def interpret(self, query, session=None, count=10, offset=0, complete=0, return_first_interpretation=True):
        """
        Call MAG Interpret API endpoint.
        Interprets a user query and returns JSON of interpretations
        see: https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/interpretmethod
        returned_JSON['interpretations'][x]['rules'][y]['output']['value'] gives value
        to query 'evaluate' for interpretation x, rule x
        e.g. x=0, y=0 will give value for 0th interpretation - i.e. use 1st result.
        """
        if session is None:
            session = self.session

        payload = {'query': query,
                   'count': count,
                   'offset': offset,
                   'complete': complete,
                   # 'timeout':5000,
                   # 'model':'latest'
                   }

        try:
            r = session.get('interpret', params=payload)
            r.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
            print(r.text)
            raise
        ret = r.json()

        # return first (most likely) interpretation value for evaluation
        if return_first_interpretation:
            ret = ret['interpretations'][0]['rules'][0]['output']['value']

        return ret

    @lru_cache(maxsize=1024)
    def evaluate(self, query, attribs='Id', session=None, count=10, offset=0):
        """
        Call MAG Evaluate API endpoint.
        Returns a set of academic entities based on query.
        Entities could be papers, authors, venues, etc.
        see: https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/evaluatemethod
        for entity attribs see: https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/entityattributes
        """

        if session is None:
            session = self.session

        payload = {'expr': query,
                   'attributes': attribs,  # 'Id' + attribs if attribs else 'Id',
                   'count': count,
                   'offset': offset,
                   # 'orderby':'name:desc',
                   # 'model':'latest'
                   }

        # Max results returned = 1000, if 1000 split, iterate by offset, combine
        # TODO: Refactor request try/except into function
        response = []
        if count > 1000:
            for i in range(0, count, 1000):
                payload = {'expr': query, 'attributes': attribs, 'count': 1000, 'offset': i}
                try:
                    if self.elapsed and self.elapsed < 1:
                        sleep(1 - self.elapsed)
                    self.start = timer()  # start timer before API call
                    req = session.get('evaluate', params=payload)
                    req.raise_for_status()
                except HTTPError as http_err:
                    print(f'HTTP error occurred: {http_err}')
                    print(req.text)
                    raise
                part = req.json()
                part = part['entities']
                response.extend(part)
                self.elapsed = timer() - self.start  # end timer before next API call
        else:
            # may sleep if we are triggering this after the previous block
            if self.elapsed and self.elapsed < 1:
                sleep(1 - self.elapsed)
            # get response and test response code
            try:
                self.start = timer()
                r = session.get('evaluate', params=payload)
                r.raise_for_status()
                self.elapsed = timer() - self.start
            except HTTPError as http_err:
                print(f'HTTP error occurred: {http_err}')
                print(payload)
                print(r.text)
                raise
            r = r.json()['entities']
            response.extend(r)

        # if len(response) == 1:
        #     response = response[0]

        return response

    # ### Utility methods
    # this could be extended for Mag API query syntax
    # https://docs.microsoft.com/en-us/azure/cognitive-services/academic-knowledge/queryexpressionsyntax
    def _make_or(self, iterable, term='Id'):
        """
        returns an OR() query for mag_api, testing several items in an iterable
        quick, hacky, serves a purpose
        """
        start = f'OR({term}='
        middle = f',{term}='.join(str(i) for i in iterable)
        end = ')'
        statement = start + middle + end
        return statement

    def _chunker(self, seq, size):
        """ returns generator of slices of seq of len(size) """
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    # ### Methods to collect papers, in and out edges
    def get_paper(self, query):
        """
        Convenience method to get one paper
        """
        if isinstance(query, str):
            query = self.interpret(query)
            if query.startswith("Ti="):
                paper = self.evaluate(query, attribs=self.ATTRIBS)
            elif query.startswith("AA."):
                print('query is an author')
                return NotImplementedError
            else:
                return NotImplementedError
        elif isinstance(query, int):
            return self.evaluate(f'Id={query}', attribs=self.ATTRIBS)[0]
        else:
            return None

    def get_refs(self, node_or_nodes, attribs=None):
        """
        Get referenced papers for this paper (node).
        node should be a paper. # TODO
        return list of dicts of paper attributes
        """
        if not attribs:
            attribs = self.ATTRIBS

        # TODO: try/except
        if isinstance(node_or_nodes, dict) and 'RId' in node_or_nodes:
            refs = node_or_nodes['RId']
        # some papers may not have references, in which case return empty list
        elif isinstance(node_or_nodes, dict) and not 'RId' in node_or_nodes:
            return []
        # elif isinstance(iterable_of_papers, (list, set, tuple, generator)):
        else:
            # refs = list(set(n for paper in node_or_nodes if 'RId' in paper for n in paper['RId']))
            ref_set = set()
            for p in node_or_nodes:
                if 'RId' in p:
                    ref_set.update(p['RId'])
            refs = list(ref_set)

        # API calls with OR() statements of len > 100? return a 404 error, so
        # Chunk longer collections, make several calls, return joined result
        max_length = 100
        if len(refs) > max_length:
            ref_papers = []
            for chunk_of_refs in self._chunker(refs, max_length):
                if self.elapsed < 1:
                    sleep(1 - self.elapsed)
                self.start = timer()
                query = self._make_or(chunk_of_refs, 'Id')
                ref_papers.extend(self.evaluate(query, count=len(chunk_of_refs), attribs=attribs))
                self.elapsed = timer() - self.start
            return ref_papers
        # simpler case - this is the underlying process to call evaluate
        else:
            query = self._make_or(refs, 'Id')
            ref_papers = self.evaluate(query, count=len(refs), attribs=attribs)
            return ref_papers

    def get_cits(self, node_or_nodes, attribs=None):
        """
        Get papers which cite this paper (node).
        node should be a paper # TODO
        return list of dicts of paper attributes
        """
        if not attribs:
            attribs = self.ATTRIBS
        # this is the pre-existing code
        # citing_papers = self.evaluate(f'RId={node["Id"]}',
        #                             count=node['CC'],
        #                             attribs=attribs)
        # return citing_papers

        # Begin with single case
        if isinstance(node_or_nodes, dict) and 'CC' in node_or_nodes:
            _Id = node_or_nodes['Id']
            _count = node_or_nodes['CC']
            return self.evaluate(f'RId={_Id}', count=_count, attribs=attribs)
        # else, if multiple papers
        else:
            max_length = 1000
            citing_papers = []
            # this will chunk items for the OR() call if greater than max_length
            for chunk in self._chunker(node_or_nodes, max_length):
                _Ids = [node['Id'] for node in chunk]
                _count = sum(node['CC'] for node in chunk)
                print(len(_Ids), _count)
                query = self._make_or(_Ids, 'RId')
                citing_papers.extend(self.evaluate(query, count=_count, attribs=attribs))
            return citing_papers


# TODO:
# - Test lru_cache is working
# - Refactor try/ except into function
# - Add utility methods for query syntax?


def build_abstract(ia):
    """Returns an abstract (str) from a MAG paper's inverted abstract"""
    l = [None] * ia['IndexLength']
    for k, v in ia['InvertedIndex'].items():
        for i in v:
            l[i] = k
    return ' '.join(filter(None, l))


def test_mag_api():
    m = Mag_Api()
    test_interpret_author = m.interpret('jaime teevan')
    assert test_interpret_author == "Composite(AA.AuN=='jaime teevan')"
    test_evaluate_previous_result = m.evaluate(test_interpret_author)
    assert len(test_evaluate_previous_result) == 10
    assert 'Id' in test_evaluate_previous_result[0]
    assert 'logprob' in test_evaluate_previous_result[0]
    first_paper = test_evaluate_previous_result[0]
    first_paper = m.get_paper(first_paper['Id'])
    author_field = first_paper['AA']
    assert any(d['AuN'] == 'jaime teevan' for d in author_field)
    print('test passed')

if __name__ == '__main__':
    test_mag_api()