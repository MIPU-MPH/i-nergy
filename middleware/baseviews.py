import sys
from tornado import ioloop, web
from tornado.concurrent import futures
from logging import getLogger
import functools
import base64
from tornado_http_auth import DigestAuthMixin, BasicAuthMixin, auth_required

logger=getLogger('middlelayer')

credentials = {
    'polimiuser':'platoon_polimi',
    'user1': 'pass1',
}

API_KEYS = {
	'rjtzWc674hDxTSWulgETRqHrVVQoI3T8f9RoMlO6zsQ': 'test'
}

def api_auth(username, password):
    if username in API_KEYS:
        return True
    #return False
    return True

def basic_auth(auth):
	def decore(f):
		def _request_auth(handler):
			handler.set_header('WWW-Authenticate', 'Basic realm=JSL')
			handler.set_status(401)
			handler.finish()
			return False
		
		@functools.wraps(f)
		def new_f(*args):
			handler = args[0]
 
			auth_header = handler.request.headers.get('Authorization')
			if auth_header is None: 
				return _request_auth(handler)
			if not auth_header.startswith('Basic '): 
				return _request_auth(handler)

			auth_decoded = base64.b64decode(auth_header[6:])#decodestring(auth_header[6:])
			username, password = str(auth_decoded).split(':', 2)
 
			if (auth(username, password)):
				f(*args)
			else:
				_request_auth(handler)
					
		return new_f
	return decore


class BaseView(web.RequestHandler):

    def prepare(self):
        self.get_authenticated_user(check_credentials_func=credentials.get, realm='Protected')

    def get(self):
        self.write('Hello %s' % self._current_user)
    # https://www.tornadoweb.org/en/stable/faq.html#why-isn-t-this-example-with-time-sleep-running-in-parallel
    # https://www.aeracode.org/2018/02/19/python-async-simplified/
    # https://opensource.com/article/18/6/tornado-framework
    def _get(self, *args, **kwargs):
        raise NotImplementedError('Implement this')

    #@basic_auth(api_auth)
    @auth_required(realm='Protected', auth_func=credentials.get)
    async def get(self, *args, **kwargs):
        """
        Creating co routine, launching async execution through a thread
        """
        executor = futures.ThreadPoolExecutor()
        try:
            # Launch sync function as async execution

            response = await ioloop.IOLoop.current().run_in_executor(
                executor, 
                self._get,
                *args,
                **kwargs,
            )
            if response is not None:
                #self.write(response)
                self.write( {'response': response})
        except web.HTTPError as why:
            msg = '{}'.format(why)
            logger.warning(msg)
            self.set_status(why.status_code, msg)
        except Exception as why:
            exctype, excmsg, exctb = sys.exc_info()
            excmsg = '{} in {} view: {}'.format(
                exctype.__name__,
                self.__class__.__name__,
                why,
                )
            logger.error(excmsg)
            self.send_error()

    def _post(self, *args, **kwargs):
       raise NotImplementedError('Implement this')

    async def post(self, *args, **kwargs):
        """
        Creating co routine, launching async execution through a thread
        """
        executor = futures.ThreadPoolExecutor()
        try:
            # Launch sync function as async execution
            response = await ioloop.IOLoop.current().run_in_executor(
                executor, 
                self._post,
                *args,
                **kwargs,
            )
            if response is not None:
                self.write(response)
        except web.HTTPError as why:
            msg = '{}'.format(why)
            self.logger.warning(msg)
            self.set_status(why.status_code, msg)
        except Exception as why:
            self.logger.error('{}'.format(why))
            self.send_error()


class NotFoundHttpException(web.HTTPError):
    
    def __init__(self, log_message=None, *args, **kwargs):
        super(NotFoundHttpException, self).__init__(
            404,
            log_message,
            *args,
            **kwargs,
        )

class MethodNotAllowedError(web.HTTPError):
    
    def __init__(self, log_message=None, *args, **kwargs):
        super(MethodNotAllowedError, self).__init__(
            405,
            log_message,
            *args,
            **kwargs,
        )
