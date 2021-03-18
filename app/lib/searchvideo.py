import requests
from bs4 import BeautifulSoup
from .opfile import allowed_file, make_path, physical2URL
import time
import os

def getvideomsg(target, url_root='http://www.javlibrary.com'):
    # url_root = 'http://www.b47w.com/cn/'
    req = requests.get(url=target)
    if not req:
        return None
    bf = BeautifulSoup(req.text,'html.parser')
    texts = bf.find_all('div', id='rightcolumn')
    title = texts[0].find(class_='post-title text')
    if not title:
        return None
    title_a = title.a
    url = url_root+title_a['href']
    name = title_a.string
    img ='http:'+texts[0].find(id='video_jacket_img')['src']
    texts = texts[0].find_all(class_='text')
    if texts:
        title_n_a = texts[0].string
        name_no = texts[1].string
        if not name_no:
            name_no = ''

        # dtime = texts[2].string
        # if not dtime:
        #     dtime = ''
        # durtime = texts[3].string
        # if not durtime:
        #     durtime = ''
        # video_director = texts[4].find('a')
        # if video_director:
        #     director = video_director.string
        # else:
        #     director = ''
        # video_maker = texts[5].find('a')
        # if video_maker:
        #     maker = video_maker.string
        # else:
        #     maker = ''
        # video_label = texts[6].find('a')
        # if video_label:
        #     label = video_label.string
        # else:
        #     label = ''
        genres = []
        video_genres = texts[8].find_all('a')
        if video_genres:
            for genre in video_genres:
                genres.append(genre.string)
        cast = []
        video_cast = texts[9].find_all('a')
        if video_cast:
            for c in video_cast:
                cast.append(c.string)
        mgs =[name,name_no,genres,cast,img]
        return mgs
    else:
        return None


def download(photo_url):
    try:
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
        imgresponse = requests.get(photo_url,headers=headers).content
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
        img_url.index('http://')
        print(img_url)
        img_url = download(img_url)
        return img_url
    except Exception as e:
        print(str(e))
        return img_url
