from elasticsearch import Elasticsearch
from ..models.esmodel import Esmodel
from math import ceil
from ..models.settings import Settings
from .. import disklist


class ESPagination(object):

    def __init__(self, page, per_page, total):
        #: the unlimited query object that was used to create this
        #: pagination object.

        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert self.query is not None, 'a query object is required ' \
                                       'for this method to work'
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):

        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

class Esvideos(object):
    # shold = []
    esmust = {"must":[]}
    # must_not = []
    # simplesearch = {}
    search_result = None

    def __init__(self,connect,timeout):
        self.es = Elasticsearch(connect,timeout=timeout)

    def keyword_search(self,keyword):
        esstr = {
            "bool":{
                "should":[
                    {
                        "match":{
                            "title": keyword
                        }           
                    },
                    {
                        "nested":{
                            "path": "actors",
                            "query":{
                                "term":{
                                    "actors.name": {
                                        "value": keyword
                                    }
                                }
                            }
                        }
                    },
                    {
                        "nested":{
                            "path": "tags",
                            "query":{
                                "term":{
                                    "tags.name": {
                                        "value": keyword
                                    }
                                }
                            }
                        }
                    }
                        
                ]
            }
        }
        self.search_result = esstr

    def nestedstr(self,classmode,value):
        esstr = {
            "nested":
            {
                "path":classmode, 
                "query":
                {
                    "term":
                    { 
                        "{0}.name".format(classmode): 
                        {
                            "value": value
                        } 
                    } 
                } 
            }
        }
        self.search_result = esstr

    def allstr(self):
        esstr = {
            "match_all":{},
        }
        self.search_result = esstr

    def start_search(self,page,size=30):
        d = {
            "query": self.search_result, 
            "from":(page-1)*size, 
            "size":size
            }
        uuidstr = self.__turnonline()
        if uuidstr:
            
            self.esmust['must'].append(self.search_result)
            self.esmust['must'].append(uuidstr)
            
            d["query"] = {'bool':self.esmust}

        print(d)
        res = self.es.search(index="mcms", body=d)
        self.esmust['must'] = []
        dlist = []
        rst = res['hits']['hits']
        for rs in rst:
            dlist.append(Esmodel(rs))
        self.pagination = ESPagination(page,size,int(res['hits']['total']))
        return dlist


    def __turnonline(self):
        sett = Settings.query.first()
        uuidlist = []
        if sett.show:
            for uuid in disklist.keys():
                uuidlist.append(uuid)
            if uuidlist:
                udict = {"terms":{
                    "uuid.keyword":uuidlist
                }}
                return udict
        return False


