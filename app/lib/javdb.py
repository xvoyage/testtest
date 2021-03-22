import requests
from bs4 import BeautifulSoup
from .langconv import * 
from .videomodel import VideoModel


class javdbmode(VideoModel):

    isdown = 0
    istoday = 0
    isyestoday = 0
    iszimu = 0
    
    root_path = [
        'https://javdb.com',
        'https://javdb8.com',
        'https://javdb7.com',
        'https://javdb6.com'
    ]

    img_list = None
    magnet = None
    videolink = None
    __xianlink = None
    
    uid = None
    videosrc = None

    @property
    def avlink(self):
        if self.__xianlink is None:
            return None
        else:
            return '/javdb{}'.format(self.__xianlink)
    @avlink.setter
    def avlink(self, value):
        self.__xianlink = value



class JavDbModeController(object):
    
    def make_javdb_request(self, url, headers=None):
        if headers is None:
            proxy_data ={
                'https://113.103.233.209:9999'
            }
            headers = {
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
            }
        # url = 'https://www.javbus.com/'
        try:
            req = requests.get(url=url, headers=headers)
            return req
        except Exception as e:
            return None


    def get_list_content(self,request):
        modelist = []
        if request is not None:
            bs = BeautifulSoup(request.text, 'html.parser')
            vlist = bs.find_all(class_='grid-item column')
            for v in vlist:
                md = javdbmode()
                md.avlink = self.get_video_href(v)
                md.title = self.get_video_title(v)
                md.fanhao = self.get_video_name(v)
                md.dtime = self.get_video_time(v)
                md.isdown = self.get_video_success(v,'tag is-success')
                md.istoday = self.get_video_success(v, 'tag is-info')
                md.iszimu = self.get_video_success(v, 'tag is-warning')
                md.samle_img = self.get_video_samle_img(v)
                modelist.append(md)

        return modelist



    def get_video_href(self,soup):
        tag_a = soup.find('a', class_='box')
        if tag_a:
            return tag_a['href']
        else:
            return None

    def get_video_title(self,soup):
        tag_title = soup.find(class_='video-title')
        if tag_title:
            return tag_title.string
        else:
            return 'N/A'

    def get_video_name(self,soup):
        tag_name = soup.find(class_='uid')
        if tag_name:
            return tag_name.string
        else:
            return 'N/A'
    def get_video_time(self,soup):
        tag_time = soup.find(class_='meta')
        if tag_time:
            return tag_time.string
        else:
            return 'N/A'

    def get_video_success(self,soup,classname):
        tag_zi = soup.find(class_=classname)
        if tag_zi:
            return 1

    def get_video_samle_img(self,soup):
        tag_img = soup.find('img')
        if tag_img:
            return tag_img['data-src']
        else:
            return 'N/A'

    def get_video_pages(self,request):
        bs = BeautifulSoup(request.text, 'html.parser')
        pages = bs.find_all(class_='pagination-link')
        active = bs.find(class_='pagination-link is-current').string
        pageslist = []
        if pages:
            for p in pages:
                status = 0
                link = '/javdb{}'.format(p['href'].replace('/',''))
                num = p.string
                if active == num:
                    status = 1
                pageslist.append((link,num,status))

        pagepre = bs.find(class_='pagination-previous')
        if pagepre:
            link = '/javdb{}'.format(pagepre['href'].replace('/',''))
            num = pagepre.string
            pageslist.append((link,num,0))

        pagenext = bs.find(class_='pagination-next')
        if pagenext:
            link = '/javdb{}'.format(pagenext['href'].replace('/',''))
            num = pagenext.string
            pageslist.append((link,num,0))
        return pageslist


    def get_show_name(self,soup):
        if soup:
            return ''.join(soup.stripped_strings)
        else:
            return 'N/A'

    def get_show_span(self,soup):
        if soup:
            return soup.string
        else:
            return 'N/A'

    def get_show_sample_href(self,soup):
        if  soup:
            href = '/javdb{}'.format(soup.a['href'])
            text = soup.a.string
            return (text, href)
        else:
            return None

    def get_show_hrefs(self,soup):
        if soup:
            actors = soup.find_all('a')
            actor_arr = []
            for a in actors:
                ahref = '/javdb{}'.format(a['href'])
                atext = a.string
                actor_arr.append((atext, ahref))
            # if not actor_arr:
            #     sp = get_show_sample_href(soup)
            return actor_arr
        else:
            return []

    def get_show_img(self,soup):
        if soup:
            img_tag = soup.find(class_='video-cover')
            if img_tag:
                return img_tag['src']
        return None

    def get_show_title(self,soup):
        title_tag = soup.find(class_='title is-4')
        if title_tag:
            return title_tag.strong.string
        return 'N/A'

    def get_show_imglist(self,soup):
        imgsdiv = soup.find(class_='tile-images preview-images')
        imglist = []
        if imgsdiv:
            imgs = imgsdiv.find_all(class_='tile-item')
            for img in imgs:
                imglist.append(img['href'])
        return imglist

    def get_show_magnet(self,soup):
        mglist = []
        
        magnetdiv = soup.find_all(class_='magnet-name')
        date = 'N/A'
        if magnetdiv:
            for magnet in magnetdiv:
                tagslist = []
                links = magnet.a['href']
                size = magnet.find(class_='meta').string
                tags = magnet.find_all(class_='tag')
                if tags:
                    for tag in tags:
                        tagslist.append(tag.string)
                vdata = magnet.next_sibling.next_sibling
                if vdata:
                    if vdata.span:
                        date = vdata.string
                mglist.append((links, tagslist, size,date))
        return mglist

    def get_show_video(self, soup):
        videotag = soup.find(id='preview-video')
        if videotag:
            if videotag.source['src']:
                videosrc = 'https:'+videotag.source['src']
                return videosrc
        return False

    def search_video_message(self,videoname):
        md = javdbmode()
        for root in md.root_path:
            try:
                linkurl = '{}/search?q={}&f=all'.format(root, videoname)
                req =self.make_javdb_request(linkurl)
                if req is not None:
                    bs = BeautifulSoup(req.text,'html.parser')
                    video_list = bs.find_all(class_='grid-item column')
                    video_url = None
                    for v in video_list:
                        vname_div = v.find(class_='uid')
                        if vname_div:
                            vname = vname_div.string
                            if vname == videoname:
                                tag_a = v.find(class_='box')
                                if tag_a:
                                    video_url = root + tag_a['href']
                                    print(video_url)
                                    break
                    if video_url is not None:
                        mreq = self.make_javdb_request(video_url)
                        md = self.get_show_main(mreq)
                        print(md.fanhao)
                        break
            except Exception as e:
                print(str(e))
        else:
            md = False

        return md
        



    def get_show_main(self,request):
        md = javdbmode()
        if request:
            bs = BeautifulSoup(request.text, 'html.parser')
            main_mg = bs.find_all(class_='panel-block')
            for mg in main_mg:
                key = mg.strong
                if key:
                    key = key.string
                    vaule = mg.find(class_='value')
                    if key == u'番號:':
                        md.fanhao = self.get_show_name(vaule)
                    if key == u'日期:':
                        md.dtime = self.get_show_span(vaule)
                    if key == u'時長:':
                        md.durtime = self.get_show_span(vaule)
                    if key == u'導演:':
                        md.daoyan = self.get_show_sample_href(vaule)
                    if key == u'片商:':
                        md.pianshang = self.get_show_sample_href(vaule)
                    if key == u'發行:':
                        md.faxing = self.get_show_sample_href(vaule)
                    if key == u'類別:':
                        md.tags = self.get_show_hrefs(vaule)
                    if key == u'演員:':
                        md.actors = self.get_show_hrefs(vaule)
                    if key == u'系列:':
                        md.xilie = self.get_show_sample_href(vaule)
            md.title = self.get_show_title(bs)
            md.samle_img = self.get_show_img(bs)
            md.img_list = self.get_show_imglist(bs)
            md.magnet = self.get_show_magnet(bs)
            md.videosrc = self.get_show_video(bs)
            
        return md



