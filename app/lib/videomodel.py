from .langconv import * 

class VideoModel(object):
    fanhao = None #番号
    title = None    #标题
    samle_img = None    #缩略图
    dtime = None    #发布时间
    durtime = None  #时长
    pianshang = None #片商
    faxing = None #发行商
    _tags = [] #标签
    _actors = [] #演员
    daoyan = None #导演
    xilie = None

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self,value):
        if not isinstance(value,list):
            raise 'type err'
        for index, v in enumerate(value):
            if not isinstance(v, tuple):
                raise 'type err'
            newword = Converter('zh-hans').convert(v[0])
            value[index] = (newword,v[1])
        self._tags = value

    @property
    def actors(self):
        return self._actors

    @actors.setter
    def actors(self,vaule):
        if not isinstance(vaule, list):
            raise 'type err'
        for v in vaule:
            if not isinstance(v,tuple):
                raise 'type err'
        self._actors = vaule

    

    def get_tags_nourl(self):
        tagslist = [x[0] for x in self._tags]
        return ';'.join(tagslist)

    def get_actors_nourl(self):
        actorslist =  [x[0] for x in self._actors]
        return ';'.join(actorslist)

    def get_daoyan_nourl(self):
        if self.daoyan is None:
            return 'N/A'
        elif isinstance(self.daoyan, tuple):
            return self.daoyan[0]
        else:
            return self.daoyan
        
    def get_pianshang_nourl(self):
        if self.pianshang is None:
            return 'N/A'
        elif isinstance(self.pianshang, tuple):
            return self.pianshang[0]
        else:
            return self.pianshang
    
    def get_xilie_nourl(self):
        if self.xilie is None:
            return 'N/A'
        elif isinstance(self.xilie, tuple):
            return self.xilie[0]
        else:
            return self.xilie

