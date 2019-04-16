LISTEN_PORT = 8000

from http.server import ThreadingHTTPServer
from RequestHandler import RequestHandler


def main():
    print('Listening on port %s' % LISTEN_PORT)
    server = ThreadingHTTPServer(('', LISTEN_PORT), RequestHandler)
    server.serve_forever()

if __name__ == '__main__':
    main()
