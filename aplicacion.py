# app.py

from apiwsgi import Wsgiclass

app = Wsgiclass()

@app.ruta("/home")
def home(request, response):
    response.text = "<h3>Pagina Home</h3>"

@app.ruta("/otra")
def otra(request, response):
    response.text = "Otra Pagina"

@app.ruta("/ultima")
def ultima(request, response):
    response.text = "Ultima Pagina"