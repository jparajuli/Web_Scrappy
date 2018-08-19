import re
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
# class impressum_url:
#     def __init__(self, base_url):
#         self.base_url = base_url
class ImpressumUrls(object):
    def __init__(self, url_lists):
        self.url_lists = url_lists
    def obtain_possible_urls(self):
        final_urls = []
        for url_list in self.url_lists:
            imp_urls = self.get_impressum_urls(url_list)
            if imp_urls !=[]:
                imp_urlss = imp_urls[-1]
                final_urls.append(imp_urlss)
        return final_urls

    def obtain_impressum_urls(self):
        final_impressums = []
        final_urls = self.obtain_possible_urls()
        for fin_url in final_urls:
            if fin_url['imp_url'].startswith('http'):
                final_impressums.append(fin_url['imp_url'])
            elif fin_url['imp_url'].startswith('/'):
                final_impressums.append('https://'+fin_url['base_url']+fin_url['imp_url'])
            else:
                pass
        return final_impressums

    def get_impressum_urls(self,base_url):
        urls = []
        urll = "https://" + base_url
        agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
        pattern =re.compile(('/impressum/|/*.*impressum|/impressum.htm*.*|/imprint|/imprint.htm*.*'))
        response = requests.get(urll, headers=agent)
        page = BeautifulSoup(response.content, 'html.parser')
        for a in page.find_all('a', href=True):
            if pattern.findall(a['href']):
                url_im = {'base_url':base_url,'imp_url': a['href']}
                urls.append(url_im)
            else:
                pass
        return urls

class LogoUrls(object):
    def __init__(self, response_a, response_div):
        self.response_a = response_a
        self.response_div = response_div
    def obtain_a_urls(self):
        a_urls = []
        a_hrefs = []
        for a in self.response_a:
            try:
                if str(a.extract()).find('logo')>0:
                    a_urls.append(a.xpath(".//img/@src").extract()[0].strip())
                    a_hrefs.append(a.xpath(".//@href").extract()[0].strip())
                else:
                    pass
            except:
                pass
        return list(set(a_urls)), list(set(a_hrefs))

    def obtain_div_urls(self):
        div_urls = []
        for d in self.response_div:
            try:
                if str(d.extract()).find('logo')>0:
                    div_urls.append(d.xpath(".//img/@src").extract()[0].strip())
                else:
                    pass
            except:
                pass
        return list(set(div_urls))


    def obtain_logo_src(self, base_url):
        logo_urls = []
        logo_hrefs=[]
        a_urls, a_hrefs = self.obtain_a_urls()
        div_urls = self.obtain_div_urls()
        for a_href in a_hrefs:
            if a_href.startswith('http'):
                logo_hrefs.append(a_href)
            elif a_href.startswith('/'):
                logo_hrefs.append(base_url+a_href)
            else:
                pass
        for a_url in a_urls:
            if a_url.startswith('http'):
                logo_urls.append(a_url)
            elif a_url.startswith('/'):
                logo_urls.append([logo_href+a_url for logo_href in logo_hrefs if fuzz.token_set_ratio(remove_puncts(a_url), remove_puncts(logo_href))>60])
            else:
                pass
        for div_url in div_urls:
            if div_url.startswith('http'):
                logo_urls.append(div_url)
            elif div_url.startswith('/'):
                logo_urls.append(base_url+div_url)
            else:
                pass
        logo_urls_new=[]
        for l in logo_urls:
             if  (l!=[]) & (type(l)==list):
                 logo_urls_new.append(l[0])
             else:
                logo_urls_new.append(l)
        logo_urls_new = list(filter(None,logo_urls_new))
        return logo_urls_new

def remove_puncts(data):
    new_data = list(filter(None, re.split(("[, \-!?:_/\.\+]+"), data)))
    new_data = ' '.join(new_data)
    return new_data
