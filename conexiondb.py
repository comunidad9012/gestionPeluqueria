import mysql.connector
from apiwsgi import Wsgiclass
from webob import Request, Response


app= Wsgiclass()


@app.ruta("/home")
def home(request, response):
    response.text=app.template("home.html")

@app.ruta("/registro")
def registroVista(request, response):
    response.text=app.template("registro.html")

@app.ruta("/logicaRegistro")
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
            response.text=app.template("registro.html", context={"error": "Ese usuario ya esta registrado"})
        elif resultado2[0] > 0:
            response.text=app.template("registro.html", context={"error": "Ese dni ya esta registrado"})
        else:
            datosCliente = (dni_cliente, nombre_cliente, apellido_cliente, telefono_cliente, usuario_cliente, contraseña_cliente)
            query = ('insert into cliente (dni_cliente, nombre_cliente, apellido_cliente, tel_cliente, usuario, contraseña) values (%s, %s, %s, %s, %s, %s)')
            cursor.execute(query, datosCliente)
            conexion.commit()
            response.text=app.template("registro.html", context={"respuesta": "Usuario cargado"})
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": "Disculpa tuvimos un problema"})
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

        fecha_actual = datetime.now()
        fecha_minima_permitida = fecha_actual + timedelta(hours=24)

        query='select count(*) from turno where dia_inicio = %s'
        cursor.execute(query, (fecha_hora_objeto,))
        respuesta=cursor.fetchone()

        if respuesta[0]>0:
            response.text=app.template("vistaAltaTurno.html", context={"respuesta": "Ese turno ya existe"})
        elif fecha_hora_objeto <= fecha_minima_permitida:
            response.text=app.template("vistaAltaTurno.html", context={"respuesta": 'Solo se permite cargar turnos con 1 dia de posterioridad'})
        else:
            queryAlta='insert into turno (dia_inicio, dia_fin, disponibilidad, dni_peluquero) values (%s,%s,%s,%s)'
            datosAlta=(fecha_hora_objeto, fechaFin,1,12345675)
            cursor.execute(queryAlta, datosAlta)
            conexion.commit()
            response.text=app.template("vistaAltaTurno.html", context={"respuesta": f'Turno {fecha_hora_objeto} cargado'})
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": "Disculpa tuvimos un problema"})
        conexion.close()

@app.ruta("/turnoConfirmado")
def turnoConfirmado(request,response):
    conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
    cursor= conexion.cursor()

    dniPeluquero=12345675
    query='SELECT idturno, dia_inicio, nombre_peluquero FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_peluquero where disponibilidad=1 and turno.dni_peluquero=%s;'
    #muestra turnos para trabajar de un peluquero
    #query='SELECT idturno, dia_inicio, nombre_peluquero FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_peluquero where disponibilidad=0 and turno.dni_peluquero=%s'
    cursor.execute(query,(dniPeluquero,))

    turno=cursor.fetchall()

    response.text=app.template("turnosConfirmados.html", context={"turnos": turno})
    conexion.close()

@app.ruta("/turnosDisponibles")
def turnosDisponibles(request,response):
    conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
    cursor= conexion.cursor()
    query='SELECT dia_inicio, nombre_peluquero, tel_peluquero FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_peluquero where disponibilidad=1;'
    
    cursor.execute(query)
    turnos=cursor.fetchall()

    response.text=app.template("turnosDisponibles.html", context={"turnos":turnos})
    conexion.close()

@app.ruta("/deleteTurno")
def deleteTurno(request,response):

    id=request.POST.get("id")
    conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
    cursor= conexion.cursor()
    datoTurno=(id,)
    query='delete from turno where idturno = %s'
    cursor.execute(query,datoTurno)
    conexion.commit()

    dniPeluquero=12345679
    query='select idturno, nombre_cliente,apellido_cliente , nombre_peluquero, dia_inicio, nombre_servicio from turnospeluqueria.turno inner join turnospeluqueria.cliente on cliente.dni_cliente = turno.dni_Cliente inner join turnospeluqueria.servicio on servicio.idservicio= turno.id_Servicio inner join turnospeluqueria.peluquero on peluquero.dni_peluquero= %s'
    cursor.execute(query,(dniPeluquero,))

    turno=cursor.fetchall()

    response.text=app.template("turnosConfirmados.html", context={"turnos": turno})
    conexion.close()


