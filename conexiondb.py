import mysql.connector
from apiwsgi import Wsgiclass
from webob import Request, Response
from datetime import datetime, timedelta
import json
import hashlib
import os

app= Wsgiclass()
sessions = {}

@app.ruta("/home")
def home(request, response):
    try:
        datosCookie = request.cookies.get('session_id')
        if datosCookie:
            datosSesion=json.loads(datosCookie)
            session_id=datosSesion.get('session_id')
            session_rol=datosSesion.get('rol')
            response.text=app.template("home.html", context={"cookieLogin": session_id, "rol":session_rol} )
        else:
            response.text=app.template("home.html")
    except Exception as e:
         response.text=app.template("userExiste.html", context={"respuesta": f"Ocurrio un problema {e}"})

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
        session_id = request.cookies.get('session_id')

        if resultado1[0] > 0:
            response.text=app.template("registro.html", context={"error": "Ese usuario ya esta registrado"})
        elif resultado2[0] > 0:
            response.text=app.template("registro.html", context={"error": "Ese dni ya esta registrado"})
        else:
            datosCliente = (dni_cliente, nombre_cliente, apellido_cliente, telefono_cliente, usuario_cliente, contraseña_cliente)
            query = ('insert into cliente (dni_cliente, nombre_cliente, apellido_cliente, tel_cliente, usuario, contraseña) values (%s, %s, %s, %s, %s, %s)')
            cursor.execute(query, datosCliente)
            conexion.commit()
            response.text=app.template("registro.html", context={"error": "Usuario registrado correctamente"})
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": "Disculpa tuvimos un problema"})
        conexion.close()

@app.ruta("/vistaAltaTurno")
def vistaAltaTurno(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        session_rol=datosSesion.get('rol')
        if session_id:
            response.text=app.template("vistaAltaTurno.html", context={"cookieLogin": session_id, "rol":session_rol})
        else:
            response.text=app.template("home.html")
    except:
        response.text=app.template("userExiste.html", context={"respuesta": "Disculpa tuvimos un problema"})

@app.ruta("/vistaTurnoConfirmado")
def vistaTurnoConfirmado(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        session_rol=datosSesion.get('rol')
        if session_id:
            response.text=app.template("vistaAltaTurno.html", context={"cookieLogin": session_id, "rol":session_rol})
        else:
            response.text=app.template("home.html")
    except:
        response.text=app.template("userExiste.html", context={"respuesta": "Disculpa tuvimos un problema"})

@app.ruta("/altaTurno")
def altaTurno(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        sessionDniPeluquero=datosSesion.get('usuario_id')
        session_rol=datosSesion.get('rol')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:       
            cursor= conexion.cursor()

            fechaInicio= request.POST.get('fechaInicio')
            fecha_hora_objeto = datetime.strptime(fechaInicio, "%Y-%m-%dT%H:%M")
            fechaFin= fecha_hora_objeto + timedelta(minutes=40)

            fecha_actual = datetime.now()
            fecha_minima_permitida = fecha_actual + timedelta(hours=24)

            query='select count(*) from turno where dia_inicio = %s and dni_Peluquero = %s'
            cursor.execute(query, (fecha_hora_objeto, sessionDniPeluquero))
            respuesta=cursor.fetchone()

            if respuesta[0]>0:
                response.text=app.template("vistaAltaTurno.html", context={"respuesta": f"El turno {fecha_hora_objeto} ya existe", "cookieLogin": session_id, "rol": session_rol})
            elif fecha_hora_objeto <= fecha_minima_permitida:
                response.text=app.template("vistaAltaTurno.html", context={"respuesta": 'Solo se permite cargar turnos con 1 dia de posterioridad', "cookieLogin": session_id, "rol": session_rol})
            else:
                queryAlta='insert into turno (dia_inicio, dia_fin, disponibilidad, dni_peluquero) values (%s,%s,%s,%s)'
                datosAlta=(fecha_hora_objeto, fechaFin,1,sessionDniPeluquero)
                cursor.execute(queryAlta, datosAlta)
                conexion.commit()
                response.text=app.template("vistaAltaTurno.html", context={"respuesta": f'Turno {fecha_hora_objeto} cargado', "cookieLogin": session_id, "rol": session_rol })
            conexion.close()
        else:
            response.text=app.template("home.html")
            conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": "Disculpa tuvimos un problema"})

@app.ruta("/editarTurnos")
def turnoConfirmado(request,response):
    conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        sessionDniPeluquero=datosSesion.get('usuario_id')
        session_rol=datosSesion.get('rol')
        if session_id:
            cursor= conexion.cursor()

            query='SELECT idturno, dia_inicio, nombre_peluquero FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_peluquero where disponibilidad=1 and turno.dni_peluquero=%s;'
            cursor.execute(query,(sessionDniPeluquero,))

            queryDelete='delete from turno where idturno = %s and disponibilidad=1'

            turnos=cursor.fetchall()
            fechaHoy = datetime.now()

            arrayTurno=[]
            
            for turno in turnos:
                if turno[1]>fechaHoy:
                    arrayTurno.append(turno)
                else:
                    cursor.execute(queryDelete,(sessionDniPeluquero,))
                    conexion.commit()

            response.text=app.template("editarTurnos.html", context={"turnos": arrayTurno, "cookieLogin": session_id, "rol":session_rol})
            conexion.close()
        else:
            response.text=app.template("home.html")
            conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema{e}", "cookieLogin": session_id, "rol":session_rol})
        conexion.close()

@app.ruta("/turnosDisponibles")
def turnosDisponibles(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        session_rol=datosSesion.get('rol')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:
            cursor= conexion.cursor()

            dniPeluquero= request.POST.get("peluquero")

            query='SELECT idturno,dia_inicio, nombre_peluquero, tel_peluquero FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_peluquero where disponibilidad=1 and turno.dni_peluquero=%s;'
            cursor.execute(query, (dniPeluquero,))
            turnos=cursor.fetchall()

            response.text=app.template("turnosDisponibles.html", context={"turnos":turnos, "cookieLogin": session_id, "rol":session_rol })
            conexion.close()
        else:
            response.text=app.template("home.html")
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema{e}", "cookieLogin": session_id, "rol":session_rol })
        conexion.close()

@app.ruta("/vistaTurnosDisponibles")
def vistaAltaTurno(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        session_rol=datosSesion.get('rol')
        if session_id:
            response.text=app.template("turnosDisponibles.html", context={"cookieLogin": session_id, "rol":session_rol})
        else:
            response.text=app.template("home.html")
    except:
        response.text=app.template("userExiste.html", context={"respuesta": "Disculpa tuvimos un problema"})

@app.ruta("/deleteTurno")
def deleteTurno(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        sessionDniPeluquero=datosSesion.get('usuario_id')
        session_rol=datosSesion.get('rol')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:
            id=request.POST.get("id")
            cursor= conexion.cursor()
            datoTurno=(id,)
            query='delete from turno where idturno = %s'
            cursor.execute(query,datoTurno)
            conexion.commit()

            query='SELECT idturno, dia_inicio, nombre_peluquero FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_peluquero where disponibilidad=1 and turno.dni_peluquero=%s;'
            cursor.execute(query,(sessionDniPeluquero,))
            turno=cursor.fetchall()
            response.text=app.template("editarTurnos.html", context={"turnos": turno, "cookieLogin": session_id, "rol":session_rol})
        else:
            response.text=app.template("home.html")
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema{e}"})
        conexion.close()

    conexion.close()

@app.ruta("/vistaEditTurno")
def vistaEditTurno(request,response):
    
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        session_rol=datosSesion.get('rol')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:
            cursor= conexion.cursor()
            query='SELECT * FROM turno where idturno = %s'
            id= request.POST.get("id")
            cursor.execute(query,(id,))
            cliente= cursor.fetchone()
            response.text=app.template("modificaTurno.html", context={"cliente":cliente, "cookieLogin": session_id, "rol":session_rol})
        else:
            response.text=app.template("home.html")

    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema ", "cookieLogin": session_id, "rol":session_rol})
    finally:
        conexion.close()

@app.ruta("/editTurno")
def editTurno(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        session_rol=datosSesion.get('rol')
        sessionDniPeluquero=datosSesion.get('usuario_id')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:
            cursor= conexion.cursor()
            idTurno= request.POST.get("idTurno")
            fechaNueva=request.POST.get('fechaInicio')
            fecha_hora_objeto = datetime.strptime(fechaNueva, "%Y-%m-%dT%H:%M")
            fechaFin= fecha_hora_objeto + timedelta(minutes=40)
            
            
            query='select count(*) from turno where dia_inicio = %s and dni_Peluquero = %s'
            cursor.execute(query, (fecha_hora_objeto, sessionDniPeluquero))
            respuesta=cursor.fetchone()

            fecha_actual = datetime.now()
            fecha_minima_permitida = fecha_actual + timedelta(hours=24)

            if fecha_hora_objeto <= fecha_minima_permitida:
                response.text=app.template("editarTurnos.html", context={"respuesta": 'Solo se permite cargar turnos con 1 dia de posterioridad', "cookieLogin": session_id,"rol": session_rol})

            elif respuesta[0]>0:
                response.text=app.template("editarTurnos.html", context={"respuesta": f"El turno {fecha_hora_objeto} ya existe", "cookieLogin": session_id,"rol": session_rol})
            else:
                queryModifica='UPDATE turno SET dia_inicio= %s, dia_fin = %s WHERE idturno=%s'
                datosmodifica=(fecha_hora_objeto, fechaFin, idTurno)
                cursor.execute(queryModifica, datosmodifica)
                response.text=app.template("editarTurnos.html", context={"respuesta": 'Turno modificado con exito', "cookieLogin": session_id, "rol": session_rol})
                conexion.commit()
        else:
            response.text=app.template("home.html")
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema{e}"})
    conexion.close()

@app.ruta("/login")
def login(request,response):
    try:
        # datosCookie = request.cookies.get('session_id')
        # datosSesion=json.loads(datosCookie)
        # session_id=datosSesion.get('session_id')   
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        cursor= conexion.cursor()
        usuario=request.POST.get("usuario")
        contraseña=request.POST.get("contraseña")

        datos=(usuario,contraseña)
        query='select dni_cliente, nombre_cliente, usuario, contraseña from cliente where usuario=%s and contraseña=%s'
        
        cursor.execute(query,datos)
        respuesta= cursor.fetchone()

        if respuesta:
            session_id = hashlib.md5(os.urandom(16)).hexdigest()
            usuario_id=respuesta[0]
            sessionDatos= {"session_id": session_id, "usuario_id": usuario_id, "rol":"usuario"}
            sessionDatosJson=json.dumps(sessionDatos)
            response.set_cookie('session_id', sessionDatosJson, secure=True, httponly=True)
            response.text=app.template("userExiste.html", context={"respuesta": f"Bienvenido {usuario}", "rol":"usuario" })
        else:
            response.text=app.template("userExiste.html", context={"respuesta": "Usuario o contraseña incorrecto"})
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema"})

@app.ruta("/vistaLogin")
def vistaLogin(request, response):
    response.text=app.template("vistaLogin.html")

@app.ruta("/logout")
def logout(request,response):
    response.delete_cookie('session_id')
    response.text=app.template("home.html")

@app.ruta("/vistaLoginAdmin")
def vistaLogin(request, response):
    response.text=app.template("vistaLoginAdmin.html")

@app.ruta("/loginAdmin")
def login(request,response):
    try:
        # datosCookie = request.cookies.get('session_id')
        # datosSesion=json.loads(datosCookie)
        # session_id=datosSesion.get('session_id')   
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        cursor= conexion.cursor()
        usuario=request.POST.get("usuario")
        contraseña=request.POST.get("contraseña")

        datos=(usuario,contraseña)
        query='select dni_peluquero, nombre_peluquero, usuario, contraseña from peluquero where usuario=%s and contraseña=%s'
        
        cursor.execute(query,datos)
        respuesta= cursor.fetchone()

        if respuesta:
            session_id = hashlib.md5(os.urandom(16)).hexdigest()
            usuario_id=respuesta[0]
            sessionDatos= {"session_id": session_id, "usuario_id": usuario_id, "rol":"admin"}
            sessionDatosJson=json.dumps(sessionDatos)
            response.set_cookie('session_id', sessionDatosJson, secure=True, httponly=True)
            response.text=app.template("userExiste.html", context={"respuesta": f"Bienvenido {usuario}",  "rol":"admin" })
        else:
            response.text=app.template("userExiste.html", context={"respuesta": "Usuario o contraseña incorrecto"})
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema"})

@app.ruta("/altaTurnoSemanal")
def altaTurnoSemanal(request, response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        sessionDniPeluquero=datosSesion.get('usuario_id')
        session_rol=datosSesion.get('rol')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:       
            cursor= conexion.cursor()

            fechaInicio=request.POST.get("fechaInicio")
            fechaFin=request.POST.get("fechaFin")
            fecha_inicio_objeto = datetime.strptime(fechaInicio, "%Y-%m-%dT%H:%M")
            fecha_fin_objeto = datetime.strptime(fechaFin, "%Y-%m-%dT%H:%M")

            if 9 <= fecha_inicio_objeto.hour <= 22 and 9 <= fecha_fin_objeto.hour <= 22 and fecha_inicio_objeto.weekday() < 5 and fecha_fin_objeto.weekday() < 5:
                 
                 duracionTurno=40

                 fecha_actual = fecha_inicio_objeto

                 while fecha_actual<=fecha_fin_objeto:
                        
                        query='select count(*) from turno where dia_inicio = %s and dni_Peluquero = %s'
                        cursor.execute(query, (fecha_actual, sessionDniPeluquero))
                        respuesta=cursor.fetchone()
                        
                        fechaFin = fecha_actual + timedelta(minutes=duracionTurno)

                        if respuesta[0] == 0:
                            queryAlta='insert into turno (dia_inicio, dia_fin, disponibilidad, dni_peluquero) values (%s,%s,%s,%s)'
                            datosAlta=(fecha_actual, fechaFin,1,sessionDniPeluquero)
                            cursor.execute(queryAlta, datosAlta)
                            conexion.commit()        
                        
                        fecha_actual += timedelta(minutes=duracionTurno)
                 response.text=app.template("vistaAltaTurno.html", context={"respuestaSemana": f'Turnos cargados{fecha_inicio_objeto.hour}', "cookieLogin": session_id, "rol": session_rol })
                 conexion.close()
            else:
                response.text=app.template("vistaAltaTurno.html", context={"respuestaSemana": 'Solo se permite cargar turnos de lunes a sábado de 9 a 22', "cookieLogin": session_id, "rol": session_rol})
        else:
            response.text=app.template("home.html")
            conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema", "cookieLogin": session_id, "rol":session_rol})

@app.ruta("/eligeTurno")
def eligeTurno(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        sessionIdUser=datosSesion.get('usuario_id')
        session_rol=datosSesion.get('rol')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:       
            cursor= conexion.cursor()
            idSeleccionado=request.POST.get("idTurno")
            query="update turno set disponibilidad = %s, dni_Cliente= %s where idturno=%s;"
            datos=(0, sessionIdUser, idSeleccionado)
            cursor.execute(query, datos)
            conexion.commit()
            response.text=app.template("turnosDisponibles.html", context={"cookieLogin": session_id, "rol": session_rol, "respuesta":"Turno reservado correctamente"})
        else:
            response.text=app.template("home.html")
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema {e}"})

@app.ruta("/turnosConfirmados")
def turnosConfirmados(request,response):
    conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        sessionDniPeluquero=datosSesion.get('usuario_id')
        session_rol=datosSesion.get('rol')
        if session_id:
            cursor= conexion.cursor()

            query='SELECT  dia_inicio, nombre_cliente, apellido_cliente, tel_cliente FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_peluquero inner join turnospeluqueria.cliente on turno.dni_Cliente=cliente.dni_cliente where disponibilidad=0 and turno.dni_peluquero=%s'
            cursor.execute(query,(sessionDniPeluquero,))

            fechaHoy = datetime.now()
            fechaAyer= fechaHoy - timedelta(days=2)
            turnos=cursor.fetchall()
            arrayTurno=[]
            arrayTurnoPasado=[]
            for turno in turnos:
                if turno[0]>fechaHoy:
                    arrayTurno.append(turno)
                elif turno[0]<fechaHoy and turno[0]>fechaAyer:
                    arrayTurnoPasado.append(turno)
            if len(arrayTurnoPasado)>=1:
                response.text=app.template("turnosConfirmados.html", context={"turnos": arrayTurno,"turnosPasados": arrayTurnoPasado, "cookieLogin": session_id, "rol":session_rol})
            else:
                response.text=app.template("turnosConfirmados.html", context={"turnos": arrayTurno,"cookieLogin": session_id, "rol":session_rol})

            conexion.close()
        else:
            response.text=app.template("home.html")
            conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema{e}", "cookieLogin": session_id, "rol":session_rol})
        conexion.close()

@app.ruta("/misTurnos")
def misTurnos(request,response):
    conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        sessionDniCliente=datosSesion.get('usuario_id')
        session_rol=datosSesion.get('rol')
        if session_id:
            cursor= conexion.cursor()

            query='SELECT  idturno ,dia_inicio, nombre_peluquero, apellido_peluquero, tel_peluquero FROM turnospeluqueria.turno inner join turnospeluqueria.peluquero on peluquero.dni_peluquero=turno.dni_Peluquero inner join turnospeluqueria.cliente on turno.dni_Cliente=cliente.dni_cliente where disponibilidad=0 and turno.dni_Cliente=%s'
            cursor.execute(query,(sessionDniCliente,))

            fechaHoy = datetime.now()

            turnos=cursor.fetchall()
            arrayTurno=[]
            for turno in turnos:
                if turno[1]>fechaHoy:
                    arrayTurno.append(turno)

            response.text=app.template("misTurnos.html", context={"turnos": arrayTurno, "cookieLogin": session_id, "rol":session_rol})
            conexion.close()
        else:
            response.text=app.template("home.html")
            conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema{e}", "cookieLogin": session_id, "rol":session_rol})
        conexion.close()

@app.ruta("/bajaTurno")
def bajaTurno(request,response):
    try:
        datosCookie = request.cookies.get('session_id')
        datosSesion=json.loads(datosCookie)
        session_id=datosSesion.get('session_id')
        session_rol=datosSesion.get('rol')
        conexion = mysql.connector.connect(host="localhost", user="mauro", password="123456", database="turnospeluqueria")
        if session_id:       
            cursor= conexion.cursor()
            idSeleccionado=request.POST.get("idTurno")
            query="update turno set disponibilidad = %s, dni_Cliente= null where idturno=%s;"
            datos=(1, idSeleccionado)
            cursor.execute(query, datos)
            conexion.commit()
            response.text=app.template("misTurnos.html", context={"cookieLogin": session_id, "rol": session_rol, "respuesta":"Turno cancelado correctamente"})
        else:
            response.text=app.template("home.html")
        conexion.close()
    except Exception as e:
        response.text=app.template("userExiste.html", context={"respuesta": f"Disculpa tuvimos un problema {e}","cookieLogin": session_id, "rol": session_rol,})
