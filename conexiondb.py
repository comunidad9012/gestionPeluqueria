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
        resultado1 = cursor.fetchone()

        queryVerifica='SELECT count(*) FROM cliente where dni_cliente = %s'
        cursor.execute(queryVerifica, (dni_cliente,))
        resultado2 = cursor.fetchone()

        if resultado1[0] > 0:
            response.text=app.template("registro.html", context={"errorUser": "Existe ese usuario"})
        elif resultado2[0] > 0:
            response.text=app.template("registro.html", context={"errorDni": "Ese dni ya esta registrado"})
        else:
            datosCliente = (dni_cliente, nombre_cliente, apellido_cliente, telefono_cliente, usuario_cliente, contraseña_cliente)
            query = ('insert into cliente (dni_cliente, nombre_cliente, apellido_cliente, tel_cliente, usuario, contraseña) values (%s, %s, %s, %s, %s, %s)')
            cursor.execute(query, datosCliente)
            conexion.commit()
            response.text=app.template("userExiste.html", context={"respuesta": "Usuario cargado"})
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": e})
        conexion.close()

@app.ruta("/vistaAltaTurno")
def vistaAltaTurno(request,response):
    response.text=app.template("vistaAltaTurno.html")

@app.ruta("/altaTurno")
def altaTurno(request,response):
    try:
        from datetime import datetime, timedelta
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        cursor= conexion.cursor()

        fechaInicio= request.POST.get('fechaInicio')
        fecha_hora_objeto = datetime.strptime(fechaInicio, "%Y-%m-%dT%H:%M")
        fechaFin= fecha_hora_objeto + timedelta(minutes=40)

        query='select count(*) from turno where dia_inicio = %s'
        cursor.execute(query, (fecha_hora_objeto,))
        respuesta=cursor.fetchone()

        if respuesta[0]>0:
            response.text=app.template("userExiste.html", context={"respuesta": "Ese turno ya existe"})
        else:
            queryAlta='insert into turno (dia_inicio, dia_fin, disponibilidad, dni_peluquero) values (%s,%s,%s,%s)'
            datosAlta=(fecha_hora_objeto, fechaFin,1,12345679)
            cursor.execute(queryAlta, datosAlta)
            conexion.commit()
            response.text=app.template("userExiste.html", context={"respuesta": f'Turno {fecha_hora_objeto} cargado'})
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": e})
        conexion.close()