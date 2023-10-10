from django.shortcuts import render
from appreservas.models import Cliente
from appreservas.models import Usuario
from appreservas.models import Arbitro
from appreservas.models import Reservaciones
from appreservas.models import Canchas
from appreservas.models import Promociones 
from django.conf import settings
from django.db import connection
from datetime import datetime
from decimal import Decimal
from datetime import date
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.db.models.functions import ExtractYear
from django.db.models.aggregates import Count

def MostrarPrincipal(request):
    rol=settings.MIS_VARIABLES_GLOBALES['rol']
    if rol=="Administrador": # type: ignore
        return render(request, 'principal.html')
    else:
        return render(request, "principalresponsable.html")
    
def CalcularResultados(request, anho,mes,cancha):
    with connection.cursor() as cursor:
        cursor.execute("SELECT (SELECT ifnull(format(sum(total),2),0) from appreservas_reservaciones where YEAR(fecha_inicio)='"+anho+"' and MONTH(fecha_inicio)='"+mes+"' and cancha_fk_id='"+cancha+"') as total,"+
                       "(SELECT ifnull(format(sum(subtotal_descuento),2),0) from appreservas_reservaciones where YEAR(fecha_inicio)='"+anho+"' and MONTH(fecha_inicio)='"+mes+"' and cancha_fk_id='"+cancha+"') as totaldescuento,"+
                       "(select count(*) from appreservas_reservaciones where YEAR(fecha_inicio)='"+anho+"' and MONTH(fecha_inicio)='"+mes+"' and cancha_fk_id='"+cancha+"' and estado='Activo') as cantidadactivas,"+
                       "(select count(*) from appreservas_reservaciones where YEAR(fecha_inicio)='"+anho+"' and MONTH(fecha_inicio)='"+mes+"' and cancha_fk_id='"+cancha+"' and estado='Cancelado') as cantidadcanceladas;")
        resultados = cursor.fetchall()
        cursor.close()
    can=Canchas.objects.all().values()
    with connection.cursor() as cursor:
        cursor.execute("SELECT YEAR(fecha_inicio) from appreservas_reservaciones GROUP BY YEAR(fecha_inicio);")
        anhos = cursor.fetchall()
        cursor.close()
    with connection.cursor() as cursor:
        cursor.execute("SELECT MONTH(fecha_inicio) from appreservas_reservaciones GROUP BY MONTH(fecha_inicio);")
        meses = cursor.fetchall()
        cursor.close()
    return render(request, 'reportes.html',{'can':can,'meses':meses,'anho':anhos,'resultados':resultados})

def MostrarReportes(request):
    can=Canchas.objects.all().values()
    mes=Reservaciones.objects.dates('fecha_inicio', 'month').distinct()
    with connection.cursor() as cursor:
        cursor.execute("SELECT YEAR(fecha_inicio) from appreservas_reservaciones GROUP BY YEAR(fecha_inicio);")
        anho = cursor.fetchall()
        cursor.close()
    with connection.cursor() as cursor:
        cursor.execute("SELECT MONTH(fecha_inicio) from appreservas_reservaciones GROUP BY MONTH(fecha_inicio);")
        mes = cursor.fetchall()
        cursor.close()
    return render(request, 'reportes.html',{'can':can,'meses':mes,'anho':anho})

def ValidarRegistrosReservas(fecha, usuario):
    with connection.cursor() as cursor:
        cursor.execute("select count(*) from appreservas_reservaciones where usuario_fk_id='"+usuario+"' and fecha_creacion LIKE'%"+fecha+"%'")
        resultado = cursor.fetchone()
        cursor.close()
        if resultado is not None and len(resultado) > 0:
            return Decimal(str(resultado[0]))
        else:
            return -1

def totalpromocion(total, fecha):
    with connection.cursor() as cursor:
        cursor.execute("SELECT TRUNCATE("+str(total)+"*((100-descuento)/100), 2) FROM appreservas_promociones WHERE '"+str(fecha)+"' >= fechainicio AND '"+str(fecha)+"'<= fechafin")
        resultado = cursor.fetchone()
        cursor.close()
        if resultado is not None and len(resultado) > 0:
            return Decimal(str(resultado[0]))
        else:
            return total  
def MostraReservaciones():
    with connection.cursor() as cursor:
        cursor.execute("select r.id, r.fecha_inicio, r.fecha_fin, r.subtotal_descuento, r.total,justificacion, r.estado, r.fecha_creacion, arb.nombre as arbitro, can.nombre as cancha, cli.nombre as cliente, usu.nombre as usuario from appreservas_reservaciones r "+
                       "left join appreservas_arbitro arb on r.arbitro_fk_id=arb.documento "+
                       "left join appreservas_canchas can on r.cancha_fk_id=can.id "+
                       "left join appreservas_cliente cli on r.cliente_fk_id=cli.documento "+
                       "left join appreservas_usuario usu on r.usuario_fk_id=usu.documento")
        resultado = cursor.fetchall()
        cursor.close()
    return resultado
def MostraReservacionesClientes():
    with connection.cursor() as cursor:
        cursor.execute("select r.id, r.fecha_inicio, r.fecha_fin, r.subtotal_descuento, r.total,justificacion, r.estado, r.fecha_creacion, arb.nombre as arbitro, can.nombre as cancha, cli.nombre as cliente, usu.nombre as usuario from appreservas_reservaciones r "+
                       "left join appreservas_arbitro arb on r.arbitro_fk_id=arb.documento "+
                       "left join appreservas_canchas can on r.cancha_fk_id=can.id "+
                       "left join appreservas_cliente cli on r.cliente_fk_id=cli.documento "+
                       "left join appreservas_usuario usu on r.usuario_fk_id=usu.documento where r.cliente_fk_id="+str(settings.MIS_VARIABLES_GLOBALES['cliente']))
        resultado = cursor.fetchall()
        cursor.close()
    return resultado
    

def HorasEnFecha(request, fecha,cancha):
    
    with connection.cursor() as cursor:
        cursor.execute("select hour(fecha_inicio), hour(fecha_fin) from appreservas_reservaciones WHERE cancha_fk_id="+cancha+" and date(fecha_inicio)='"+fecha+"' and estado='Activo' order by hour(fecha_inicio);")
        resultado = cursor.fetchall()
        cursor.close()
        nueva_lista = []
        for tupla in resultado:
            for hora in range(tupla[0], tupla[1]+1):
                nueva_lista.append(hora)
    canchas=Canchas.objects.all().values()
    return render(request, 'reservar_cancha.html', {'horas':nueva_lista, 'factual':fecha,'can':canchas, 'canchita':int(cancha)})

def HorasEnFechaUsuario(request, fecha,cancha):
    
    with connection.cursor() as cursor:
        cursor.execute("select hour(fecha_inicio), hour(fecha_fin) from appreservas_reservaciones WHERE cancha_fk_id="+cancha+" and date(fecha_inicio)='"+fecha+"' and estado='Activo' order by hour(fecha_inicio);")
        resultado = cursor.fetchall()
        cursor.close()
        nueva_lista = []
        for tupla in resultado:
            for hora in range(tupla[0], tupla[1]+1):
                nueva_lista.append(hora)
    canchas=Canchas.objects.all().values()
    return render(request, 'reservar_canchausuario.html', {'horas':nueva_lista, 'factual':fecha,'can':canchas, 'canchita':int(cancha)})


def SumarUnDia(request, fecha,cancha):
    fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
    nueva_fecha = fecha_datetime + timedelta(days=1)
    nueva_fecha_str = nueva_fecha.strftime('%Y-%m-%d')
    return HorasEnFecha(request, HttpResponse(nueva_fecha_str).content.decode(),cancha)

def RestarUnDia(request, fecha,cancha):
    fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
    nueva_fecha = fecha_datetime - timedelta(days=1)
    nueva_fecha_str = nueva_fecha.strftime('%Y-%m-%d')
    return HorasEnFecha(request, HttpResponse(nueva_fecha_str).content.decode(),cancha)
def SumarUnDiaUsuario(request, fecha,cancha):
    fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
    nueva_fecha = fecha_datetime + timedelta(days=1)
    nueva_fecha_str = nueva_fecha.strftime('%Y-%m-%d')
    return HorasEnFechaUsuario(request, HttpResponse(nueva_fecha_str).content.decode(),cancha)

def RestarUnDiaUsuario(request, fecha,cancha):
    fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d')
    nueva_fecha = fecha_datetime - timedelta(days=1)
    nueva_fecha_str = nueva_fecha.strftime('%Y-%m-%d')
    return HorasEnFechaUsuario(request, HttpResponse(nueva_fecha_str).content.decode(),cancha)

def convertirfecha(fecha):
    my_datetime = datetime.strptime(''+fecha, '%Y-%m-%dT%H:%M')
    print(fecha)
    return my_datetime




def MostrarLogin(request):
    return render(request, "index.html")
def MostrarRegistrar(request):
    return render(request, "registrar.html")
def ModalRegistro(request, hora, cancha, fecha):
    return render(request, "modalregistro.html", {'ccancha':cancha, 'ttotal':Canchas.objects.get(id=cancha).costo,'hhora':hora, 'arb':Arbitro.objects.all().values(),
                                                  'canchita':cancha, 'factual':fecha})
def ModalRegistroUsuario(request, hora, cancha, fecha):
    return render(request, "modalregistrousuario.html", {'ccancha':cancha, 'ttotal':Canchas.objects.get(id=cancha).costo,'hhora':hora, 'arb':Arbitro.objects.all().values(),
                                                  'canchita':cancha, 'factual':fecha, 'cli':Cliente.objects.all().values()})


def MostrarListarClientes(request):
    return render(request, 'listar_clientes.html',{'datoscli':Cliente.objects.all().values()})
def MostrarListarUsuarios(request):
    return render(request, 'listar_usuarios.html',{'datosusu':Usuario.objects.all().values()})
def MostrarListarEscenarios(request):
    return render(request, 'listar_escenarios.html',{'datoscan': Canchas.objects.all().values()})
def MostrarListarArbitros(request):
    return render(request, 'listar_arbitros.html', {'datosarb': Arbitro.objects.all().values()})
def MostrarListarPromociones(request):
    return render(request, 'listar_promociones.html', {'datospro': Promociones.objects.all().values()})
def MostrarListarReservaciones(request):
    return render(request, 'listar_reservaciones.html', {'datosres':MostraReservaciones(),'factual':(date.today().strftime('%Y-%m-%d'))})
def MostrarClienteListarReservaciones(request):
    return render(request, 'listarreservacionesclientes.html', {'datosres':MostraReservacionesClientes(),'factual':(date.today().strftime('%Y-%m-%d'))})
def MostrarListarReservacionesCliente(request,fecha,cancha):
    return HorasEnFecha(request, fecha, cancha) # type: ignore
def MostrarListarReservacionesUsuario(request,fecha,cancha):
    return HorasEnFechaUsuario(request, fecha, cancha) # type: ignore


def RegistrarClientes(request):
    return render(request,'registrar_clientes.html')
def RegistrarUsuarios(request):
    return render(request,'registrar_usuarios.html')
def RegistrarEscenarios(request):
    return render(request,'registrar_escenarios.html')
def RegistrarArbitros(request):
    return render(request,'registrar_arbitros.html')
def RegistrarPromociones(request):
    return render(request,'registrar_promociones.html')
def RegistrarReservaciones(request):
    can=Canchas.objects.all().values()
    cli=Cliente.objects.all().values()
    pro=Promociones.objects.all().values()
    arb=Arbitro.objects.all().values()
    datos={'can':can,'cli':cli,'pro':pro,'arb':arb}
    return render(request,'registrar_reservaciones.html',datos)



def ActualizarClientes(request,documento):
    return render(request, 'actualizar_clientes.html',{'cli':Cliente.objects.get(documento=documento)})
def ActualizarUsuarios(request,documento):
    return render(request, 'actualizar_usuarios.html',{'usu':Usuario.objects.get(documento=documento)})
def ActualizarEscenarios(request,codigo):
    return render(request, 'actualizar_escenarios.html',{'can':Canchas.objects.get(id=codigo)})
def ActualizarArbitros(request,documento):
    return render(request, 'actualizar_arbitros.html',{'arb':Arbitro.objects.get(documento=documento)})
def ActualizarPromociones(request,codigo):
    return render(request, 'actualizar_promociones.html',{'pro':Promociones.objects.get(id=codigo)})
def ActualizarReservaciones(request,codigo):
    can=Canchas.objects.all().values()
    cli=Cliente.objects.all().values()
    pro=Promociones.objects.all().values()
    arb=Arbitro.objects.all().values()
    res=Reservaciones.objects.get(id=codigo)
    datos={'can':can,'cli':cli,'pro':pro,'arb':arb, 'res':res}
    return render(request, 'actualizar_reservaciones.html',datos)










def InsertarClientes(request):
        if request.method=='POST':
            try:
                doc=request.POST['documento']
                nom=request.POST['nombre']
                ape=request.POST['apellido']
                dir=request.POST['direccion']
                cor=request.POST['correo_electronico']
                con=request.POST['contrasena']
                cli=Cliente(documento=doc, nombre=nom, apellido=ape, direccion=dir, correo=cor, contasena=con)
                cli.save()
                datos={'r':'Registro Exitoso'}
                return render(request, 'registrar_clientes.html', datos)
            except:
                datos={'r': 'Datos Erroneos, intente nuevamente.'}
                return render(request, 'registrar_clientes.html',datos)
        else:
            datos={'r': 'Accion no valida'}
            return render(request, 'registrar_clientes.html',datos)

def InsertarRegistroClientes(request):
        if request.method=='POST':
            try:
                doc=request.POST['documento']
                nom=request.POST['nombre']
                ape=request.POST['apellido']
                dir=request.POST['direccion']
                cor=request.POST['correo_electronico']
                con=request.POST['contrasena']
                cli=Cliente(documento=doc, nombre=nom, apellido=ape, direccion=dir, correo=cor, contasena=con)
                cli.save()
                datos={'r':'Registro Exitoso'}
                return render(request, 'index.html', datos)
            except:
                datos={'r': 'Datos Erroneos, intente nuevamente.'}
                return render(request, 'registrar.html',datos)
        else:
            datos={'r': 'Accion no valida'}
            return render(request, 'registrar.html',datos)  

def InsertarUsuario(request):
        if request.method=='POST':
            try:
                doc=request.POST['documento']
                nom=request.POST['nombre']
                ape=request.POST['apellido']
                dir=request.POST['direccion']
                cor=request.POST['correo_electronico']
                con=request.POST['contrasena']
                rol=request.POST['rol']
                registros=request.POST['registros']
                usu=Usuario(documento=doc, nombre=nom, apellido=ape, direccion=dir, correo=cor, contasena=con, rol=rol, registropordia=registros)
                usu.save()
                datos={'r':'Registro Exitoso'}
                return render(request, 'registrar_usuarios.html', datos)
            except:
                datos={'r': 'Datos Erroneos, intente nuevamente.'}
                return render(request, 'registrar_usuarios.html',datos)
        else:
            datos={'r': 'Accion no valida'}
            return render(request, 'registrar_usuarios.html',datos)  
        
def InsertarEscenarios(request):
        if request.method=='POST':
            try:
                nom=request.POST['nombre']
                dix=request.POST['dimensionx']
                diy=request.POST['dimensiony']
                cos=request.POST['costo']
                can=Canchas(nombre=nom, dimension_x=dix, dimension_y=diy, costo=cos)
                can.save()
                datos={'r':'Registro Exitoso'}
                return render(request, 'registrar_escenarios.html', datos)
            except:
                datos={'r': 'Datos Erroneos, intente nuevamente.'}
                return render(request, 'registrar_escenarios.html',datos)
        else:
            datos={'r': 'Accion no valida'}
            return render(request, 'registrar_escenarios.html',datos)  
        
def InsertarArbitros(request):
        if request.method=='POST':
            try:
                doc=request.POST['documento']
                nom=request.POST['nombre']
                ape=request.POST['apellido']
                tel=request.POST['telefono']
                cor=request.POST['correo_electronico']
                cost=request.POST['costo']
                arb=Arbitro(documento=doc, nombre=nom, apellido=ape, telefono=tel, correo=cor,costo=cost)
                arb.save()
                datos={'r':'Registro Exitoso'}
                return render(request, 'registrar_arbitros.html', datos)
            except:
                datos={'r': 'Datos Erroneos, intente nuevamente.'}
                return render(request, 'registrar_arbitros.html',datos)
        else:
            datos={'r': 'Accion no valida'}
            return render(request, 'registrar_arbitros.html',datos)  
        
def InsertarPromociones(request):
        if request.method=='POST':
            try:
                nom=request.POST['nombre']
                ini=request.POST['fechainicio']
                fin=request.POST['fechafin']
                des=request.POST['descuento']
                pro=Promociones(nombre=nom, fechainicio=ini, fechafin=fin, descuento=des)
                pro.save()
                datos={'r':'Registro Exitoso'}
                return render(request, 'registrar_promociones.html', datos)
            except:
                datos={'r': 'Datos Erroneos, intente nuevamente.'}
                return render(request, 'registrar_promociones.html',datos)
        else:
            datos={'r': 'Accion no valida'}
            return render(request, 'registrar_promociones.html',datos)  
        
def InsertarReservaciones(request):
        canc=Canchas.objects.all().values()
        clie=Cliente.objects.all().values()
        prom=Promociones.objects.all().values()
        arbi=Arbitro.objects.all().values()
        if request.method=='POST':
            try:
                can=request.POST['cancha']
                cli=request.POST['cliente']
                arb=request.POST['arbitro']
                ini=request.POST['fechainicio']
                fin=request.POST['fechafin']
                jus=request.POST['justificacion']
                total=request.POST['total']
                fechabuscar=convertirfecha(ini)
                decuentopromocion=totalpromocion(total, fechabuscar, can)
                usuario = settings.MIS_VARIABLES_GLOBALES['usuario']
                res=Reservaciones(cancha_fk_id=can,cliente_fk_id=cli,arbitro_fk_id=arb,usuario_fk_id=usuario,
                                  fecha_inicio=ini,fecha_fin=fin,subtotal_descuento=decuentopromocion,total=total, justificacion=jus, estado="Activo")
                res.save()
                datos={'r':'Registro Exitoso','can':canc,'cli':clie,'pro':prom,'arb':arbi}
                return render(request, 'registrar_reservaciones.html', datos)
            except:
                datos={'r':'Datos erroneos, intente nuevamente','can':canc,'cli':clie,'pro':prom,'arb':arbi}
                return render(request, 'registrar_reservaciones.html', datos)
        else:
            datos={'r': 'Accion no valida','can':canc,'cli':clie,'pro':prom,'arb':arbi}
            return render(request, 'registrar_reservaciones.html',datos)  
        
def InsertarReservacionesClientes(request,canchita,fecha):
        if request.method=='POST':
            try:
                can=canchita
                cli=settings.MIS_VARIABLES_GLOBALES['cliente']
                arb=request.POST['arbitro']
                hora_inicio = request.POST['fechainicio']
                ini = datetime.strptime(fecha + ' ' + hora_inicio + ':00', '%Y-%m-%d %H:%M:%S')
                fin=ini + timedelta(hours=(int(request.POST['fechafin'])-1))
                total=request.POST['total']
                decuentopromocion=totalpromocion(total, ini)
                if arb=="Sin Arbitro":
                    res=Reservaciones(cancha_fk_id=can,cliente_fk_id=cli,
                                  fecha_inicio=ini,fecha_fin=fin,subtotal_descuento=decuentopromocion,total=total, estado="Activo")
                    res.save()
                else:
                    res=Reservaciones(cancha_fk_id=can,cliente_fk_id=cli,arbitro_fk_id=arb,
                                  fecha_inicio=ini,fecha_fin=fin,subtotal_descuento=decuentopromocion,total=total, estado="Activo")
                    res.save()
                return MostrarListarReservacionesCliente(request,fecha,canchita)
            except:
                return MostrarListarReservacionesCliente(request,fecha,canchita)
        else:
            return MostrarListarReservacionesCliente(request,fecha,canchita)
        
def InsertarReservacionesUsuarios(request,canchita,fecha):
    rolll= settings.MIS_VARIABLES_GLOBALES['rol']
    usuario = settings.MIS_VARIABLES_GLOBALES['usuario']
    cantidadregistropermitidos=settings.MIS_VARIABLES_GLOBALES['cantreg']
    cantidadregistrosingresados=ValidarRegistrosReservas((date.today().strftime('%Y-%m-%d')), str(usuario))
    if rolll =='Administrador' or ((cantidadregistrosingresados>=0 and cantidadregistrosingresados<cantidadregistropermitidos) and rolll == 'Responsable'):
        if request.method=='POST':
            try:
                can=canchita
                arb=request.POST['arbitro']
                cli=request.POST['cliente']
                hora_inicio = request.POST['fechainicio']
                ini = datetime.strptime(fecha + ' ' + hora_inicio + ':00', '%Y-%m-%d %H:%M:%S')
                fin=ini + timedelta(hours=(int(request.POST['fechafin'])-1))
                jus=request.POST['justificacion']
                total=request.POST['total']
                decuentopromocion=totalpromocion(total, ini)
                if arb=="Sin Arbitro":
                    res=Reservaciones(cancha_fk_id=can,cliente_fk_id=cli,usuario_fk_id=usuario,
                                fecha_inicio=ini,fecha_fin=fin,subtotal_descuento=decuentopromocion,total=total, justificacion=jus, estado="Activo")
                    res.save()
                else:
                    res=Reservaciones(cancha_fk_id=can,cliente_fk_id=cli,arbitro_fk_id=arb,usuario_fk_id=usuario,
                                fecha_inicio=ini,fecha_fin=fin,subtotal_descuento=decuentopromocion,total=total, justificacion=jus, estado="Activo")
                    res.save()
                return MostrarListarReservacionesUsuario(request,fecha,canchita)
            except:
                return MostrarListarReservacionesUsuario(request,fecha,canchita)
        else:
            return MostrarListarReservacionesUsuario(request,fecha,canchita)
    else:
        return MostrarListarReservacionesUsuario(request,fecha,canchita)







def ModificarClientes(request,documento):
        if request.method=='POST':
            try:
                doc=request.POST['documento']
                nom=request.POST['nombre']
                ape=request.POST['apellido']
                dir=request.POST['direccion']
                cor=request.POST['correo_electronico']
                con=request.POST['contrasena']
                cli=Cliente.objects.get(documento=documento)
                cli.documento=doc
                cli.nombre=nom
                cli.apellido=ape
                cli.direccion=dir
                cli.correo=cor
                cli.contasena=con
                cli.save()
                cli=Cliente.objects.all().values()
                datos={'r':'Actualizacion Exitosa',
                       'datoscli':cli}
                return render(request, 'listar_clientes.html', datos)
            except:
                cli=Cliente.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datoscli':cli}
                return render(request, 'listar_clientes.html',datos)
        else:
            cli=Cliente.objects.all().values()
            datos={'r': 'Accion no valida','datoscli':cli}
            return render(request, 'listar_clientes.html',datos)  

def ModificarUsuario(request,documento):
        if request.method=='POST':
            try:
                doc=request.POST['documento']
                nom=request.POST['nombre']
                ape=request.POST['apellido']
                dir=request.POST['direccion']
                cor=request.POST['correo_electronico']
                con=request.POST['contrasena']
                roll=request.POST['rol']
                registros=request.POST['registros']
                usu=Usuario.objects.get(documento=documento)
                usu.documento=doc
                usu.nombre=nom
                usu.apellido=ape
                usu.direccion=dir
                usu.correo=cor
                usu.contasena=con
                usu.rol=roll
                usu.registropordia=registros
                usu.save()
                usu=Usuario.objects.all().values()
                datos={'r':'Actualizacion Exitosa','datosusu':usu}
                return render(request, 'listar_usuarios.html', datos)
            except:
                usu=Usuario.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datosusu':usu}
                return render(request, 'listar_usuarios.html',datos)
        else:
            usu=Usuario.objects.all().values()
            datos={'r': 'Accion no valida','datosusu':usu}
            return render(request, 'listar_usuarios.html',datos)  
        
def ModificarEscenarios(request, id):
        if request.method=='POST':
            try:
                nom=request.POST['nombre']
                dix=request.POST['dimensionx']
                diy=request.POST['dimensiony']
                cos=request.POST['costo']
                can=Canchas.objects.get(id=id)
                can.nombre=nom
                can.dimension_x=dix
                can.dimension_y=diy
                can.costo=cos
                can.save()
                can=Canchas.objects.all().values()
                datos={'r':'Actualizacion Exitosa', 'datoscan':can}
                return render(request, 'listar_escenarios.html', datos)
            except:
                can=Canchas.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.', 'datoscan':can}
                return render(request, 'listar_escenarios.html',datos)
        else:
            can=Canchas.objects.all().values()
            datos={'r': 'Accion no valida', 'datoscan':can}
            return render(request, 'listar_escenarios.html',datos)  
        
def ModificarArbitros(request,documento):
        if request.method=='POST':
            try:
                doc=request.POST['documento']
                nom=request.POST['nombre']
                ape=request.POST['apellido']
                tel=request.POST['telefono']
                cor=request.POST['correo_electronico']
                cost=request.POST['costo']
                arb=Arbitro.objects.get(documento=documento)
                arb.documento=doc
                arb.nombre=nom
                arb.apellido=ape
                arb.telefono=tel
                arb.correo=cor
                arb.costo=cost
                arb.save()
                arb=Arbitro.objects.all().values()
                datos={'r':'Actualizacion Exitosa','datosarb':arb}
                return render(request, 'listar_arbitros.html', datos)
            except:
                arb=Arbitro.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datosarb':arb}
                return render(request, 'listar_arbitros.html',datos)
        else:
            arb=Arbitro.objects.all().values()
            datos={'r': 'Accion no valida','datosarb':arb}
            return render(request, 'listar_arbitros.html',datos)  
        
def ModificarPromociones(request,id):
        if request.method=='POST':
            try:
                nom=request.POST['nombre']
                ini=request.POST['fechainicio']
                fin=request.POST['fechafin']
                des=request.POST['descuento']
                pro=Promociones.objects.get(id=id)
                pro.nombre=nom
                pro.fechainicio=ini
                pro.fechafin=fin
                pro.descuento=des
                pro.save()
                pro=Promociones.objects.all().values()
                datos={'r':'Actualizacion Exitosa','datospro':pro}
                return render(request, 'listar_promociones.html', datos)
            except:
                pro=Promociones.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datospro':pro}
                return render(request, 'listar_promociones.html',datos)
        else:
            pro=Promociones.objects.all().values()
            datos={'r': 'Accion no valida','datospro':pro}
            return render(request, 'listar_promociones.html',datos)  
        
def ModificarReservaciones(request,id):
        canc=Canchas.objects.all().values()
        clie=Cliente.objects.all().values()
        prom=Promociones.objects.all().values()
        arbi=Arbitro.objects.all().values()
        if request.method=='POST':
            try:
                can=request.POST['cancha']
                cli=request.POST['cliente']
                arb=request.POST['arbitro']
                ini=request.POST['fechainicio']
                fin=request.POST['fechafin']
                jus=request.POST['justificacion']
                totalcancha=(Canchas.objects.get(id=can)).costo
                fechabuscar=convertirfecha(ini)
                decuentopromocion=totalpromocion(totalcancha, fechabuscar, can)
                usuario = settings.MIS_VARIABLES_GLOBALES['usuario']
                res=Reservaciones.objects.get(id=id)
                res.cancha_fk_id=can # type: ignore
                res.cliente_fk_id=cli # type: ignore
                res.arbitro_fk_id=arb # type: ignore
                res.usuario_fk_id=usuario # type: ignore
                res.fecha_inicio=ini
                res.fecha_fin=fin
                res.subtotal_descuento=Decimal(str(decuentopromocion)) # type: ignore
                res.total=totalcancha
                res.justificacion=jus
                res.estado="Activo"
                res.save()
                res=MostraReservaciones()
                datos={'r':'Actualizacion Exitosa','can':canc,'cli':clie,'pro':prom,'arb':arbi,'datosres':res}
                return render(request, 'listar_reservaciones.html', datos)
            except:
                res=MostraReservaciones()
                datos={'r':'Datos erroneos, intente nuevamente','can':canc,'cli':clie,'pro':prom,'arb':arbi, 'datosres':res}
                return render(request, 'listar_reservaciones.html', datos)
        else:
            res=MostraReservaciones()
            datos={'r': 'Accion no valida','can':canc,'cli':clie,'pro':prom,'arb':arbi, "datosres":res}
            return render(request, 'listar_reservaciones.html',datos)  










def EliminarClientes(request,documento):
            try:
                cli=Cliente.objects.get(documento=documento)
                cli.delete()
                cli=Cliente.objects.all().values()
                datos={'r':'Eliminacion Exitosa',
                       'datoscli':cli}
                return render(request, 'listar_clientes.html', datos)
            except:
                cli=Cliente.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datoscli':cli}
                return render(request, 'listar_clientes.html',datos)
def EliminarUsuario(request,documento):
            try:
                usu=Usuario.objects.get(documento=documento)
                usu.delete()
                usu=Usuario.objects.all().values()
                datos={'r':'Eliminacion Exitosa','datosusu':usu}
                return render(request, 'listar_usuarios.html', datos)
            except:
                usu=Usuario.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datosusu':usu}
                return render(request, 'listar_usuarios.html',datos)
        
def EliminarEscenarios(request, id):
            try:
                can=Canchas.objects.get(id=id)
                can.delete()
                can=Canchas.objects.all().values()
                datos={'r':'Eliminacion Exitosa', 'datoscan':can}
                return render(request, 'listar_escenarios.html', datos)
            except:
                can=Canchas.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.', 'datoscan':can}
                return render(request, 'listar_escenarios.html',datos) 
        
def EliminarArbitros(request,documento):
            try:
                arb=Arbitro.objects.get(documento=documento)
                arb.delete()
                arb=Arbitro.objects.all().values()
                datos={'r':'Eliminacion Exitosa','datosarb':arb}
                return render(request, 'listar_arbitros.html', datos)
            except:
                arb=Arbitro.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datosarb':arb}
                return render(request, 'listar_arbitros.html',datos)
        
def EliminarPromociones(request,id):
            try:
                pro=Promociones.objects.get(id=id)
                pro.delete()
                pro=Promociones.objects.all().values()
                datos={'r':'Eliminacion Exitosa','datospro':pro}
                return render(request, 'listar_promociones.html', datos)
            except:
                pro=Promociones.objects.all().values()
                datos={'r': 'Datos Erroneos, intente nuevamente.','datospro':pro}
                return render(request, 'listar_promociones.html',datos) 
        
def EliminarReservaciones(request,id):
        try:
                res=Reservaciones.objects.get(id=id)
                res.delete()
                return MostrarListarReservaciones(request)
        except:
                return MostrarListarReservaciones(request)
        
def EliminarReservacionesCliente(request,id,justificacion):
        try:
                res=Reservaciones.objects.get(id=id)
                res.justificacion=justificacion
                res.estado="Cancelado"
                res.save()
                return MostrarClienteListarReservaciones(request)
        except:
                return MostrarClienteListarReservaciones(request)
        









def FiltrarClientes(request, busqueda, columna):
     try:
        datos=Cliente.objects.all().values()
        if columna=="Documento":
            datos=Cliente.objects.filter(documento__contains=busqueda)
        if columna=="Nombre":
            datos=Cliente.objects.filter(nombre__contains=busqueda)
        if columna=="Apellido":
            datos=Cliente.objects.filter(apellido__contains=busqueda)
        if columna=="Direccion":
            datos=Cliente.objects.filter(direccion__contains=busqueda)
        if columna=="Correo":
            datos=Cliente.objects.filter(correo__contains=busqueda)
        if not datos:
            datos=Cliente.objects.all().values();
        return render(request,"listar_clientes.html",   {'datoscli':datos})
     except:
        return render(request,"listar_clientes.html",{'datoscli':Cliente.objects.all().values()})
def FiltrarUsuarios(request, busqueda, columna):
     try:
        datos=Usuario.objects.all().values()
        if columna=="Documento":
            datos=Usuario.objects.filter(documento__contains=busqueda)
        if columna=="Nombre":
            datos=Usuario.objects.filter(nombre__contains=busqueda)
        if columna=="Apellido":
            datos=Usuario.objects.filter(apellido__contains=busqueda)
        if columna=="Direccion":
            datos=Usuario.objects.filter(direccion__contains=busqueda)
        if columna=="Correo":
            datos=Usuario.objects.filter(correo__contains=busqueda)
        if not datos:
            datos=Usuario.objects.all().values();
        return render(request,"listar_usuarios.html",   {'datosusu':datos})
     except:
        return render(request,"listar_usuarios.html",{'datosusu':Usuario.objects.all().values()})
def FiltrarArbitros(request, busqueda, columna):
     try:
        datos=Arbitro.objects.all().values()
        if columna=="Documento":
            datos=Arbitro.objects.filter(documento__contains=busqueda)
        if columna=="Nombre":
            datos=Arbitro.objects.filter(nombre__contains=busqueda)
        if columna=="Apellido":
            datos=Arbitro.objects.filter(apellido__contains=busqueda)
        if columna=="Telefono":
            datos=Arbitro.objects.filter(telefono__contains=busqueda)
        if columna=="Correo":
            datos=Arbitro.objects.filter(correo__contains=busqueda)
        if not datos:
            datos=Arbitro.objects.all().values();
        return render(request,"listar_arbitros.html",   {'datosarb':datos})
     except:
        return render(request,"listar_arbitros.html",{'datosabr':Arbitro.objects.all().values()})
def FiltrarEscenarios(request, busqueda, columna):
     try:
        datos=Canchas.objects.all().values()
        if columna=="Codigo":
            datos=Canchas.objects.filter(id__contains=busqueda)
        if columna=="Nombre":
            datos=Canchas.objects.filter(nombre__contains=busqueda)
        if not datos:
            datos=Canchas.objects.all().values();
        return render(request,"listar_escenarios.html",   {'datoscan':datos})
     except:
        return render(request,"listar_escenarios.html",{'datoscan':Canchas.objects.all().values()})
def FiltrarPromociones(request, busqueda, columna):
     try:
        datos=Promociones.objects.all().values()
        if columna=="Codigo":
            datos=Promociones.objects.filter(id__contains=busqueda)
        if columna=="Nombre":
            datos=Promociones.objects.filter(nombre__contains=busqueda)
        if not datos:
            datos=Promociones.objects.all().values();
        return render(request,"listar_promociones.html",   {'datospro':datos})
     except:
        return render(request,"listar_promociones.html",{'datospro':Promociones.objects.all().values()})
def FiltrarReservaciones(request, busqueda, columna):
    with connection.cursor() as cursor:
        if busqueda!="ninguno":
            cursor.execute("select r.id, r.fecha_inicio, r.fecha_fin, r.subtotal_descuento, r.total,justificacion, r.estado, r.fecha_creacion, arb.nombre as arbitro, can.nombre as cancha, cli.nombre as cliente, usu.nombre as usuario from appreservas_reservaciones r "+
                       "left join appreservas_arbitro arb on r.arbitro_fk_id=arb.documento "+
                       "left join appreservas_canchas can on r.cancha_fk_id=can.id "+
                       "left join appreservas_cliente cli on r.cliente_fk_id=cli.documento "+
                       "left join appreservas_usuario usu on r.usuario_fk_id=usu.documento where "+columna+" like '%"+busqueda+"%'")
        else:
             cursor.execute("select r.id, r.fecha_inicio, r.fecha_fin, r.subtotal_descuento, r.total,justificacion, r.estado, r.fecha_creacion, arb.nombre as arbitro, can.nombre as cancha, cli.nombre as cliente, usu.nombre as usuario from appreservas_reservaciones r "+
                       "left join appreservas_arbitro arb on r.arbitro_fk_id=arb.documento "+
                       "left join appreservas_canchas can on r.cancha_fk_id=can.id "+
                       "left join appreservas_cliente cli on r.cliente_fk_id=cli.documento "+
                       "left join appreservas_usuario usu on r.usuario_fk_id=usu.documento")
        resultado = cursor.fetchall()
        cursor.close()
    return render(request, 'listar_reservaciones.html', {'datosres':resultado,'factual':(date.today().strftime('%Y-%m-%d'))}) 

def FiltrarReservacionesCliente(request, busqueda, columna):
    with connection.cursor() as cursor:
        if busqueda!="ninguno":
            cursor.execute("select r.id, r.fecha_inicio, r.fecha_fin, r.subtotal_descuento, r.total,justificacion, r.estado, r.fecha_creacion, arb.nombre as arbitro, can.nombre as cancha, cli.nombre as cliente, usu.nombre as usuario from appreservas_reservaciones r "+
                       "left join appreservas_arbitro arb on r.arbitro_fk_id=arb.documento "+
                       "left join appreservas_canchas can on r.cancha_fk_id=can.id "+
                       "left join appreservas_cliente cli on r.cliente_fk_id=cli.documento "+
                       "left join appreservas_usuario usu on r.usuario_fk_id=usu.documento where "+columna+" like '%"+busqueda+"%' and r.cliente_fk_id="+str(settings.MIS_VARIABLES_GLOBALES['cliente']))
        else:
             cursor.execute("select r.id, r.fecha_inicio, r.fecha_fin, r.subtotal_descuento, r.total,justificacion, r.estado, r.fecha_creacion, arb.nombre as arbitro, can.nombre as cancha, cli.nombre as cliente, usu.nombre as usuario from appreservas_reservaciones r "+
                       "left join appreservas_arbitro arb on r.arbitro_fk_id=arb.documento "+
                       "left join appreservas_canchas can on r.cancha_fk_id=can.id "+
                       "left join appreservas_cliente cli on r.cliente_fk_id=cli.documento "+
                       "left join appreservas_usuario usu on r.usuario_fk_id=usu.documento where r.cliente_fk_id="+str(settings.MIS_VARIABLES_GLOBALES['cliente']))
        resultado = cursor.fetchall()
        cursor.close()
    return render(request, 'listarreservacionesclientes.html', {'datosres':resultado,'factual':(date.today().strftime('%Y-%m-%d'))})









def IniciarLogin(request):
        if request.method=='POST':
            try:
                tipo=request.POST['tipo']
                cor=request.POST['correo']
                con=request.POST['contrasena']
                if tipo=='usuario':
                    datos=Usuario.objects.filter(correo=cor, contasena=con)
                    if not datos:
                        return render(request, 'index.html', {'r':'Datos Erroneos'})
                    else:
                        settings.MIS_VARIABLES_GLOBALES['usuario'] = datos.first().documento # type: ignore
                        settings.MIS_VARIABLES_GLOBALES['rol'] = datos.first().rol # type: ignore
                        settings.MIS_VARIABLES_GLOBALES['cantreg'] = datos.first().registropordia # type: ignore
                        if datos.first().rol=="Administrador": # type: ignore
                             return render(request, 'principal.html')
                        else:
                             return render(request, "principalresponsable.html")
                else:
                    datos=Cliente.objects.filter(correo=cor, contasena=con)
                    if not datos:
                        return render(request, 'index.html', {'r':'Datos Erroneos'})
                    else:
                        settings.MIS_VARIABLES_GLOBALES['cliente'] = datos.first().documento # type: ignore
                        #return HorasEnFecha(request, (date.today().strftime('%Y-%m-%d')),str(Canchas.objects.first().id)) # type: ignore
                        return MostrarClienteListarReservaciones(request)
            except:
                return render(request, 'index.html',{'r': 'Datos Erroneos, intente nuevamente.'})
        else:
                return render(request, 'index.html',{'r': 'Accion no valida.'})
            
