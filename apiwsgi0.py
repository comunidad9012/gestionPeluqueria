# api Wsgi con server wsgi


class Wsgiclass:
    def __call__(self, environ, start_response):
        response_body = b"Hola Mundo"
        status = "200 OK"
        start_response(status, headers=[])
        return iter([response_body])