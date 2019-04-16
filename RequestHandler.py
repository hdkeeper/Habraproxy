import requests
import re
from http.server import BaseHTTPRequestHandler
from bs4 import BeautifulSoup


TARGET_SITE = 'habr.com'
IGNORE_HEADERS = ['content-encoding']
IGNORE_TAGS = ['script']

RE_HABR_REF = re.compile(r'^https://habr\.com')
RE_ALTER_WORD = re.compile(r'\b(\w{6})\b')


class RequestHandler(BaseHTTPRequestHandler):
    @property
    def target_url(self):
        return 'https://%s%s' % (TARGET_SITE, self.path)

    @property
    def target_headers(self):
        h = dict(self.headers)
        h['Host'] = TARGET_SITE
        return h

    def do_GET(self):
        r = requests.get(self.target_url,
            headers=self.target_headers,
            allow_redirects=False)
        self.process_response(r)

    def do_HEAD(self):
        r = requests.head(self.target_url,
            headers=self.target_headers)
        self.process_response(r)

    def do_POST(self):
        r = requests.post(self.target_url,
            headers=self.target_headers,
            data=self.rfile.read(),
            allow_redirects=False)
        self.process_response(r)


    def process_response(self, r):
        'Обработка полученного ответа'
        if r.status_code == requests.codes.ok:
            content = r.content
            if r.headers['Content-Type'].startswith('text/html'):
                content = self.alter_html(content)

            self.send_response(r.status_code)
            for (h, v) in r.headers.items():
                if h.lower() not in IGNORE_HEADERS:
                    self.send_header(h, v)

            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        
        else:
            self.send_response(r.status_code)
            for (h, v) in r.headers.items():
                self.send_header(h, v)
            self.end_headers()
            

    def alter_html(self, source):
        'Внести изменения в HTML'

        def change_link(el, attr):
            'Изменяем ссылку в атрибуте элемента'
            if attr in el.attrs:
                el[attr] = re.sub(RE_HABR_REF, '', el[attr])

        doc = BeautifulSoup(source, 'html5lib')
        for el in doc.find_all('a'):
            change_link(el, 'href')

        for el in doc.find_all('use'):
            change_link(el, 'xlink:href')

        for el in doc.body.find_all(string=RE_ALTER_WORD):
            if el.parent.name.lower() not in IGNORE_TAGS:
                el.replace_with(re.sub(RE_ALTER_WORD, u'\\1™', el.string))

        return doc.encode('utf-8')
