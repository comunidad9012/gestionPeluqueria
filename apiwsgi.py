# api Wsgi con server wsgi

from webob import Request, Response


class Wsgiclass:
    def __init__(self):
        self.rutas = {}

    def __call__(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    def ruta(self, path):
        def wrapper(controlador):
            self.rutas[path] = controlador
            return controlador

        return wrapper

    def handle_request(self, request):
        response = Response()

        for path, controlador in self.rutas.items():
            if path == request.path:
                controlador(request, response)
                return response

        self.default_response(response)
        return response
    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Pagina no encontrada"