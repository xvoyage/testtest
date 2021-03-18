import requests
from bs4 import BeautifulSoup


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


def get_list_mgs(request):
    htmldos={}
    bs = BeautifulSoup(request.text, 'html.parser')
    mainhtml = bs.find('div', id='waterfall')
    edit = edit_href(mainhtml)
    htmldos['main'] = str(edit)
    foothtml = bs.find('div', class_='text-center hidden-xs')
    footer = get_list_pages(foothtml)
    htmldos['footer'] = str(footer)
    return htmldos


def get_list_pages(htmlnode):
    tag_a = htmlnode.find_all('a')
    for a in tag_a:
        hreftext = str(a['href'])
        num = hreftext.split('/')[-1]
        href = '/javbuslist?page={0}'.format(num)
        a['href'] = href
    return str(htmlnode)
        


def get_xs_link(htmlnode):
    tag_a = htmlnode.find(class_='movie-box')
    if tag_a:
        return tag_a['href']
    return '---'

def get_list_img(htmlnode):
    tag_img = htmlnode.find(class_='movie-box')
    img = tag_img.find('img')
    if img:
        return img['src']
    else:
        return '---'

def edit_href(htmlnode):
    tag_as = htmlnode.find_all(class_='movie-box')
    for a in tag_as:
        hreftext = str(a['href'])
        a['href'] = hreftext.replace('https://www.javbus.com/','/javbus/')
        a['target'] = '_blank'
    return str(htmlnode)


def get_movie_mg(request, Referer):
    htmldos={}
    bs = BeautifulSoup(request.text, 'html.parser')
    mainhtml = bs.find('div', class_='container')
    title = get_moive_title(mainhtml)
    htmldos['title'] = str(title)
    htmldos['main'] = get_movie_content(mainhtml)
    # htmldos['download'] = get_download_link(mainhtml)
    htmldos['imgs'] = get_movies_imgs(mainhtml)
    # htmldos['script'] = get_script(request)
    url = _get_cili_url(bs)
    htmldos['magnet'] = get_magnet(url,Referer)
    return htmldos


def get_moive_title(htmldos):
    title = htmldos.find('h3')
    if title:
        return str(title)
    else:
        return '---'

def get_movie_content(htmldos):
    cmain = htmldos.find(class_='row movie')
    if cmain:
        return str(cmain)
    else:
        return '---'
def get_download_link(htmldos):
    dlink = htmldos.find(id='magnet-table')
    if dlink:
        return str(dlink)
    else:
        return '---'

def get_movies_imgs(htmldos):
    imgs = htmldos.find(id='sample-waterfall')
    if imgs:
        tag_a = imgs.find_all(class_='sample-box')
        for a in tag_a:
            img = a.find('img')
            img['data-original'] = a['href']
            a['href'] = '#'
        return str(imgs)
    else:
        return '---'

def get_script(request):
    bs = BeautifulSoup(request.text,'html.parser')
    sc = bs.find_all('script')
    return str(sc[8])

def _get_cili_url(soup):
    """get_cili(soup).get the ajax url and Referer url of request"""

    ajax_get_cili_url = 'https://www.javbus.com/ajax/uncledatoolsbyajax.php?lang=zh'
    ajax_data = soup.select('script')[8].string
    for l in ajax_data.split(';')[:-1]:
        ajax_get_cili_url += '&%s' % l[7:].replace("'","").replace(' ','')
    return ajax_get_cili_url

def get_magnet(url,Referer):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
        'Host':'www.javbus.com',
        'Connection':'close',
        'X-Requested-With':'XMLHttpRequest',
        'Referer':Referer
    }
    req = make_request(url, headers=headers)
    return str(req.text)
    