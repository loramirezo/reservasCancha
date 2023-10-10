"""
URL configuration for reservacancha project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from appreservas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.MostrarLogin),
    path('mostrarregistrar', views.MostrarRegistrar),
    path('mostrarprincipal', views.MostrarPrincipal),
    path('mostrarreportes', views.MostrarReportes),
    path('calcularresultados/<str:anho>/<str:mes>/<str:cancha>', views.CalcularResultados),
    path('iniciarlogin', views.IniciarLogin),
    path('modalregistro/<str:hora>/<str:cancha>/<str:fecha>', views.ModalRegistro),
    path('modalregistrousuario/<str:hora>/<str:cancha>/<str:fecha>', views.ModalRegistroUsuario),
    path('horasenfecha/<str:fecha>/<str:cancha>',views.HorasEnFecha),
    path('horasenfechausuario/<str:fecha>/<str:cancha>',views.HorasEnFechaUsuario),
    path('sumarundia/<str:fecha>/<str:cancha>',views.SumarUnDia),
    path('restarundia/<str:fecha>/<str:cancha>',views.RestarUnDia),
    path('sumarundiausuario/<str:fecha>/<str:cancha>',views.SumarUnDiaUsuario),
    path('restarundiausuario/<str:fecha>/<str:cancha>',views.RestarUnDiaUsuario),

    path('mostrarlistarclientes',views.MostrarListarClientes),
    path('mostrarlistarusuarios',views.MostrarListarUsuarios),
    path('mostrarlistarescenarios',views.MostrarListarEscenarios),
    path('mostrarlistararbitros',views.MostrarListarArbitros),
    path('mostrarlistarpromociones',views.MostrarListarPromociones),
    path('mostrarlistarreservaciones',views.MostrarListarReservaciones),
    path('mostrarclientelistarreservaciones',views.MostrarClienteListarReservaciones),
    path('mostrarlistarreservacionescliente/<str:fecha>/<str:cancha>',views.MostrarListarReservacionesCliente),
    path('mostrarlistarreservacionesusuario/<str:fecha>/<str:cancha>',views.MostrarListarReservacionesUsuario),
    
    path('mostrarregistrarclientes',views.RegistrarClientes),
    path('mostrarregistrarusuarios',views.RegistrarUsuarios),
    path('mostrarregistrarescenarios',views.RegistrarEscenarios),
    path('mostrarregistrararbitros',views.RegistrarArbitros),
    path('mostrarregistrarpromociones',views.RegistrarPromociones),
    path('mostrarregistrarreservaciones',views.RegistrarReservaciones),

    path('mostraractualizarclientes/<int:documento>',views.ActualizarClientes),
    path('mostraractualizarusuarios/<int:documento>',views.ActualizarUsuarios),
    path('mostraractualizarescenarios/<int:codigo>',views.ActualizarEscenarios),
    path('mostraractualizararbitros/<int:documento>',views.ActualizarArbitros),
    path('mostraractualizarpromociones/<int:codigo>',views.ActualizarPromociones),
    path('mostraractualizarreservaciones/<int:codigo>',views.ActualizarReservaciones),

    path('insertarclientes',views.InsertarClientes),
    path('insertarregistroclientes',views.InsertarRegistroClientes),
    path('insertarusuarios',views.InsertarUsuario),
    path('insertarescenarios',views.InsertarEscenarios),
    path('insertararbitros',views.InsertarArbitros),
    path('insertarpromociones',views.InsertarPromociones),
    path('insertarreservaciones',views.InsertarReservaciones),
    path('insertarreservacionesclientes/<str:canchita>/<str:fecha>',views.InsertarReservacionesClientes),
    path('insertarreservacionesusuarios/<str:canchita>/<str:fecha>',views.InsertarReservacionesUsuarios),
    
    path('modificarclientes/<int:documento>', views.ModificarClientes),
    path('modificarusuarios/<int:documento>', views.ModificarUsuario),
    path('modificarescenarios/<int:id>', views.ModificarEscenarios),
    path('modificararbitros/<int:documento>', views.ModificarArbitros),
    path('modificarpromociones/<int:id>', views.ModificarPromociones),
    path('modificarreservaciones/<int:id>', views.ModificarReservaciones),

    path('eliminarclientes/<int:documento>', views.EliminarClientes),
    path('eliminarusuarios/<int:documento>', views.EliminarUsuario),
    path('eliminarescenarios/<int:id>', views.EliminarEscenarios),
    path('eliminararbitros/<int:documento>', views.EliminarArbitros),
    path('eliminarpromociones/<int:id>', views.EliminarPromociones),
    path('eliminarreservaciones/<int:id>', views.EliminarReservaciones),
    path('eliminarreservacionescliente/<int:id>/<str:justificacion>', views.EliminarReservacionesCliente),

    path('filtrarclientes/<str:busqueda>/<str:columna>', views.FiltrarClientes),
    path('filtrarusuarios/<str:busqueda>/<str:columna>', views.FiltrarUsuarios),
    path('filtrararbitros/<str:busqueda>/<str:columna>', views.FiltrarArbitros),
    path('filtrarescenarios/<str:busqueda>/<str:columna>', views.FiltrarEscenarios),
    path('filtrarpromociones/<str:busqueda>/<str:columna>', views.FiltrarPromociones),
    path('filtrarreservaciones/<str:busqueda>/<str:columna>', views.FiltrarReservaciones),
    path('filtrarreservacionescliente/<str:busqueda>/<str:columna>', views.FiltrarReservacionesCliente)
]
