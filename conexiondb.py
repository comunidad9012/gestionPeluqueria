import mysql.connector
from apiwsgi import Wsgiclass
from webob import Request, Response


app= Wsgiclass()


@app.ruta("/home")
def registroVista(request, response):
    response.text=app.template("home.html")

@app.ruta("/registro")
def registroVista(request, response):
    response.text=app.template("registro.html")

@app.ruta("/logicaAlta")
def logicaAlta(request, response):

    try:    
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        cursor= conexion.cursor()

        nombre_cliente = request.POST.get('nombreCliente')
        apellido_cliente = request.POST.get('apellidoCliente')
        dni_cliente = request.POST.get('dniCliente')
        telefono_cliente = request.POST.get('Telefono')
        usuario_cliente = request.POST.get('usuarioCliente')
        contraseña_cliente = request.POST.get('contraseña')

        queryVerifica='SELECT count(*) FROM cliente where usuario = %s'
        cursor.execute(queryVerifica, (usuario_cliente,))
        resultado = cursor.fetchone()

        if resultado[0] > 0:
            response.text=app.template("home.html")
        else:
            datosCliente = (dni_cliente, nombre_cliente, apellido_cliente, telefono_cliente, usuario_cliente, contraseña_cliente)
            query = ('insert into cliente (dni_cliente, nombre_cliente, apellido_cliente, tel_cliente, usuario, contraseña) values (%s, %s, %s, %s, %s, %s)')

            cursor.execute(query, datosCliente)
            conexion.commit()
        response.text=app.template("home.html")
    except Exception as e:
        response.text=app.template("home.html")
        conexion.close()

