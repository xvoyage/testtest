from .. import disklist
import os

class Estag(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Esvideotimes(object):
    def __init__(self, id, time, imgurl):
        self.id = id
        self.time = time
        self.imgurl = imgurl

class Esmodel(object):


    @property
    def tags(self):
        if not self._tags or self._tags is None:
            return None
        return self._tags

    @tags.setter
    def tags(self, values):
        if not values or values is None:
            self._tags = None
        else:
            self._tags = self.__make_property(values)

    @property
    def actors(self):
        if not self._actors or self._actors is None:
            return None
        return self._actors 

    @actors.setter
    def actors(self, values):
        if not values or values is None:
            self._actors = None
        else:
            self._actors = self.__make_property(values)

    
    @property
    def cate(self):
        if not self._cate or self._cate is None:
            return None
        return self._cate

    @cate.setter
    def cate(self, value):
        if not value or value is None:
            self._cate = None
        else:
            self._cate = self.__simple_property(value)

    @property
    def director(self):
        if not self._director or self._director is None:
            return None
        return self._director

    @director.setter
    def director(self, value):
        if not value or value is None:
            self._director = None
        else:
            self._director = self.__simple_property(value)

    @property
    def producer(self):
        if not self._producer or self._producer is None:
            return None
        return self._producer

    @producer.setter
    def producer(self, value):
        if not value or value is None:
            self._producer = None
        else:
            self._producer = self.__simple_property(value)

    @property
    def series(self):
        if not self._series or self._series is None:
            return None
        return self._series

    @series.setter
    def series(self, value):
        if not value or value is None:
            self._series = None
        else:
            self._series = self.__simple_property(value)

    @property
    def video_times(self):
        if not self._video_times or self._video_times is None:
            return None
        return self._video_times 

    @video_times.setter
    def video_times(self, values):
        if not values or values is None:
            self._video_times = None
        else:
            tagslist = []
            if not isinstance(values, list):
                raise 'err'
            for v in values:
                if not isinstance(v,dict):
                    raise 'err'
                tagslist.append(Esvideotimes(v.get('id',None), v.get('time',None), v.get('imgurl',None)))
            return tagslist



    def __simple_property(self,value):
        if not isinstance(value, dict):
                raise 'err'
        return Estag(value.get('id',None), value.get('name',None))


    def __make_property(self, values):
        tagslist = []
        if not isinstance(values, list):
            raise 'err'
        for v in values:
            if not isinstance(v,dict):
                raise 'err'
            tagslist.append(Estag(v.get('id',None), v.get('name',None)))
        return tagslist


    def __init__(self, values):
        self.__init_model(values)

    def __init_model(self, values):
        self.id = values.get('_id',None)
        self.title = values['_source'].get('title',None)
        self.cate = values['_source'].get('cate',None)
        self.director = values['_source'].get('director',None)
        self.producer = values['_source'].get('producer',None)
        self.series = values['_source'].get('series',None)
        self.name = values['_source'].get('name',None)
        self.img = values['_source'].get('img',None)
        self.stats = values['_source'].get('stats',None)
        self.movie_file = values['_source'].get('movie_file',None)
        self.description = values['_source'].get('description',None)
        self.video_times = values['_source'].get('video_times',None)
        self.ares = values['_source'].get('ares',None)
        self.splitfile = values['_source'].get('splitfile',None)
        self.pypath = values['_source'].get('pypath',None)
        self.hashpath = values['_source'].get('hashpath',None)
        self.size = values['_source'].get('size',None)
        self.sceen = values['_source'].get('sceen',None)
        self.uuid = values['_source'].get('uuid',None)
        self.chinese = values['_source'].get('chinese',None)
        self.date = values['_source'].get('date',None)
        self.durtime = values['_source'].get('durtime',None)
        self.perview = values['_source'].get('perview',None)
        self.tags = values['_source'].get('tags',None)
        self.actors = values['_source'].get('actors',None)


    def isonline(self):
        disk = disklist.get(self.uuid,None)
        if disk is not None:
            pypath = '{}{}'.format(disk, self.pypath)
            hashpath = '{}{}'.format(disk,self.hashpath)
            pyf = os.path.exists(pypath)
            hsf = os.path.exists(hashpath)
            if pyf or hsf:
                return True
        return False

    def ishd(self):
        pass



