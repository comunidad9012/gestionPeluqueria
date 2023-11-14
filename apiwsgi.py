from webob import Request, Response
from jinja2 import Environment, FileSystemLoader

class Wsgiclass:

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def __init__(self, templates_dir="templates"):
        self.dic_rutas = {}
        
        self.templates_env = Environment(
            loader = FileSystemLoader(templates_dir)
        )
    
    def template(self, template_name, context=None):
        if context is None:
            context = {}
        return self.templates_env.get_template(template_name).render(**context)

    def ruta(self, path):
        def envoltura(controlador):
            self.dic_rutas[path] = controlador
            return controlador

        return envoltura

    def handle_request(self, request):
        response = Response()

        for path, controlador in self.dic_rutas.items():
            if path == request.path:
                controlador(request, response)
                return response

        self.default_response(response)
        return response
    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Pagina no encontrada"