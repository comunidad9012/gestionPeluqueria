import os
from webob import Request, Response
from jinja2 import Environment, FileSystemLoader

class Wsgiclass:

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def __init__(self, templates_dir="templates", static_dir="static"):
        self.dic_rutas = {}
        self.static_dir = static_dir
        
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

        if request.path.startswith('/static/'):
            static_path = os.path.join(self.static_dir, request.path[8:])
            static_path = os.path.abspath(static_path)
            if static_path.startswith(os.path.abspath(os.path.join(self.static_dir, 'images'))):
                if os.path.exists(static_path) and os.path.isfile(static_path):
                    with open(static_path, 'rb') as f:
                        response.body = f.read()
                    response.content_type = self.get_content_type(static_path)
                    return response

        # Resto del manejo de rutas
        for path, controlador in self.dic_rutas.items():
            if path == request.path:
                controlador(request, response)
                return response

        self.default_response(response)
        return response
    
    def default_response(self, response):
        response.status_code = 404
        response.text = "Pagina no encontrada"

    def get_content_type(self, file_path):
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        if ext == '.png':
            return 'image/png'
        elif ext == '.jpg' or ext == '.jpeg':
            return 'image/jpeg'
        elif ext == '.gif':
            return 'image/gif'
        elif ext == '.html':
            return 'text/html'
        else:
            return 'application/octet-stream'