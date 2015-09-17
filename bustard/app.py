#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import httplib

from .router import Router
from .wsgi_server import make_server

NOTFOUND_HTML = """
<html>
    <h1>404 Not Found</h1>
</html>
"""


class Bustard(object):
    def __init__(self):
        self._route = Router()

    def __call__(self, environ, start_response):
        """for wsgi server"""
        self.start_response = start_response
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']

        print(path, method)
        print(self._route.methods)
        func = self._route.get_func(path, method)

        if func is None:
            return self.notfound()

        result = func()
        if isinstance(result, (list, tuple)):
            status, data, headers = result
        else:
            status, data, headers = 200, result, None

        return self.make_response(data, status, headers)

    def make_response(self, body, code=200, headers=None,
                      content_type='text/html'):
        status_code = str(code) + ' ' + httplib.responses.get(code)
        headers = {} if headers is None else headers
        headers.setdefault('Content-Type', content_type)
        header_list = headers.items()
        self.start_response(status_code, header_list)
        return [body]

    def route(self, path, methods=None):

        def wrapper(func):
            self._route.register(path, func, methods)
            return func

        return wrapper

    def notfound(self):
        return self.make_response(NOTFOUND_HTML, code=404)

    def run(self, host='127.0.0.1', port=5000):
        address = (host, port)
        httpd = make_server(address, self)
        print('WSGIServer: Serving HTTP on %s ...\n' % str(address))
        httpd.serve_forever()
