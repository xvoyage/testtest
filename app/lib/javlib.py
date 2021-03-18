import requests
from bs4 import BeautifulSoup
from .opfile import allowed_file, make_path, physical2URL
import time
import os
from .videomodel import VideoModel


def make_request(url, headers=None):
    if headers is None:
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
        }
    # url = 'https://www.javbus.com/'
    try:
        req = requests.get(url=url, headers=headers)
        return req
    except Exception as e:
        return None

def get_video_meg(request):
    video = VideoModel()
    bs = BeautifulSoup(request.text, 'html.parser')
    
    main = bs.find('div',id='rightcolumn')
    video.samle_img = get_video_img(main)
    mg_items = main.find_all(class_='item')
    titel = main.find(class_='post-title text')
    video.title = get_video_tltle(titel)
    for mgitem in mg_items:
        header = mgitem.find(class_='header').string
        if header == u'识别码:':
            video.fanhao = get_show_nohref(mgitem)
        if header == u'发行日期:':
            video.dtime = get_show_nohref(mgitem)
        if header == u'导演:':
            video.daoyan = get_show_sample_href(mgitem)
        if header == u'制作商:':
            video.pianshang = get_show_sample_href(mgitem)
        if header == u'发行商:':
            video.faxing = get_show_sample_href(mgitem)
        if header == u'类别:':
            video.tags = get_show_hrefs(mgitem)
        if header == u'演员:':
            video.actors = get_show_hrefs(mgitem)
    return video

def javlib_search_video_msg(videoname):
    url = 'http://www.b47w.com/cn/vl_searchbyid.php?&keyword={0}'.format(videoname)
    req = make_request(url)
    if req:
        return get_video_meg(req)
    return None


def get_video_tltle(soup):
    title = soup.find('a')
    if title:
        return title.string
    else:
        return 'N/A'


def get_video_img(soup):
    img = 'http:'+soup.find(id='video_jacket_img')['src']
    if img:
        return img;
    else:
        return False

def get_show_nohref(soup):
    try:
        text = soup.find(class_='text').string
        return text
    except Exception as e:
        return 'N/A'
def get_show_sample_href(soup):
    try:
        text_class = soup.find(class_='text')
        a_tag = text_class.find('a')
        return (a_tag.string,a_tag['href'])
    except Exception as e:
        return ('N/A',0)

def get_show_hrefs(soup):
    hlist = []
    try:
        text_class = soup.find(class_='text')
        a_tags = text_class.find_all('a')
        for tc in a_tags:
            hlist.append((tc.string, tc['href']))
    except Exception as e:
        pass
    return hlist







def download(photo_url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
        st = time.time()
        imgresponse = requests.get(photo_url,headers=headers).content
        print('方法内下载图片时间{}'.format(time.time()-st))
        dirname = allowed_file(photo_url)
        if dirname:
            path = make_path(dirname)
            extend = photo_url.split('.')[-1]
            name = str(int(round(time.time()* 1000)))
            filename = name + '.' + extend
            fullpath = os.path.join(path,filename)

        with open(fullpath, 'wb') as f:
            f.write(imgresponse)
        return physical2URL(fullpath)
    except Exception as e:
        return photo_url

def checkimgurl(url):
    img_url = url
    try:
        img_url.index('https://')
        print(img_url)
        img_url = download(img_url)
        return img_url
    except Exception as e:
        print(str(e))
        return img_url