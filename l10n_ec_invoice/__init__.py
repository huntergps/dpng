# -*- coding: utf-8 -*-

from . import controllers
from . import models

import threading
import time

import odoo
import psycopg2
import werkzeug.exceptions
from odoo.http import HttpRequest, Response, Root, request


def request_cors_headers():
    old_http_dispatch = HttpRequest.dispatch

    def set_default(self, template=None, qcontext=None, uid=None):
        self.template = template
        self.qcontext = qcontext or dict()
        self.qcontext['response_template'] = self.template
        self.uid = uid
        # Support for Cross-Origin Resource Sharing
        if request.endpoint:
            if 'cors' in request.endpoint.routing:
                self.headers.set('Access-Control-Allow-Origin', request.endpoint.routing['cors'])
                methods = 'GET, POST'
                if request.endpoint.routing['type'] == 'json':
                    methods = 'POST'
                elif request.endpoint.routing.get('methods'):
                    methods = ', '.join(request.endpoint.routing['methods'])
                self.headers.set('Access-Control-Allow-Methods', methods)
            elif request.endpoint.routing['type'] == 'json':
                self.headers.set('Access-Control-Allow-Credentials', 'true')
                self.headers.set('Access-Control-Allow-Origin', request.httprequest.headers.get('ORIGIN'))

    def http_dispatch(self):
        if request.httprequest.method == 'OPTIONS' and request.endpoint:
            headers = {
                'Access-Control-Max-Age': 60 * 60 * 24,
                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, X-Debug-Mode'
            }
            return Response(status=200, headers=headers)
        else:
            return old_http_dispatch(self)


    def root_dispatch(self, environ, start_response):
        """
        Performs the actual WSGI dispatching for the application.
        """
        try:
            httprequest = werkzeug.wrappers.Request(environ)
            httprequest.app = self
            httprequest.parameter_storage_class = werkzeug.datastructures.ImmutableOrderedMultiDict
            threading.current_thread().url = httprequest.url
            threading.current_thread().query_count = 0
            threading.current_thread().query_time = 0
            threading.current_thread().perf_t0 = time.time()

            explicit_session = self.setup_session(httprequest)
            self.setup_db(httprequest)
            self.setup_lang(httprequest)
            global request
            request = self.get_request(httprequest)

            def _dispatch_nodb():
                try:
                    func, arguments = self.nodb_routing_map.bind_to_environ(request.httprequest.environ).match()
                except werkzeug.exceptions.HTTPException as e:
                    return request._handle_exception(e)
                request.set_handler(func, arguments, "none")
                result = request.dispatch()
                return result

            with request:
                db = request.session.db
                if db:
                    try:
                        odoo.registry(db).check_signaling()
                        with odoo.tools.mute_logger('odoo.sql_db'):
                            ir_http = request.registry['ir.http']
                    except (AttributeError, psycopg2.OperationalError, psycopg2.ProgrammingError):
                        # psycopg2 error or attribute error while constructing
                        # the registry. That means either
                        # - the database probably does not exists anymore
                        # - the database is corrupted
                        # - the database version doesnt match the server version
                        # Log the user out and fall back to nodb
                        request.session.logout()
                        # If requesting /web this will loop
                        if request.httprequest.path == '/web':
                            result = werkzeug.utils.redirect('/web/database/selector')
                        else:
                            result = _dispatch_nodb()
                    else:
                        if request.httprequest.method == 'OPTIONS':
                            headers = {
                                'Access-Control-Allow-Credentials': 'true',
                                'Access-Control-Allow-Origin': request.httprequest.headers.get('ORIGIN'),
                                'Access-Control-Max-Age': 60 * 60 * 24,
                                'Access-Control-Allow-Headers': 'Origin, X-Requested-With, Content-Type, Accept, X-Debug-Mode'
                            }
                            result = Response(status=200, headers=headers)
                        else:
                            result = ir_http._dispatch()
                else:
                    result = _dispatch_nodb()

                response = self.get_response(httprequest, result, explicit_session)
            return response(environ, start_response)

        except werkzeug.exceptions.HTTPException as e:
            return e(environ, start_response)

    Response.set_default = set_default
    HttpRequest.dispatch = http_dispatch
    Root.dispatch = root_dispatch
