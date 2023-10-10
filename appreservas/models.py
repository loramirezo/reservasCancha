from django.db import models

class Cliente(models.Model):
    documento=models.IntegerField(primary_key=True)
    nombre=models.CharField(max_length=100)
    apellido=models.CharField(max_length=100)
    direccion=models.CharField(max_length=200)
    correo=models.CharField(max_length=150)
    contasena=models.CharField(max_length=100)

class Usuario(models.Model):
    documento=models.IntegerField(primary_key=True)
    nombre=models.CharField(max_length=100)
    apellido=models.CharField(max_length=100)
    direccion=models.CharField(max_length=200)
    correo=models.CharField(max_length=150)
    contasena=models.CharField(max_length=100)
    rol=models.CharField(max_length=100)
    registropordia=models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)

class Arbitro(models.Model):
    documento=models.IntegerField(primary_key=True)
    nombre=models.CharField(max_length=100)
    apellido=models.CharField(max_length=100)
    telefono=models.CharField(max_length=200)
    correo=models.CharField(max_length=150)
    costo=models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    
class Canchas(models.Model):
    nombre=models.CharField(max_length=100)
    dimension_x=models.DecimalField(max_digits=10, decimal_places=2)
    dimension_y=models.DecimalField(max_digits=10, decimal_places=2)
    costo=models.DecimalField(max_digits=10, decimal_places=2)

class Promociones(models.Model):
    nombre=models.CharField(max_length=100)
    fechainicio=models.DateTimeField()
    fechafin=models.DateTimeField()
    descuento=models.DecimalField(max_digits=10, decimal_places=2)

class Reservaciones(models.Model):
    cancha_fk = models.ForeignKey(Canchas, on_delete=models.CASCADE)
    cliente_fk = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descuento_fk=models.ForeignKey(Promociones, null=True, blank=True, on_delete=models.SET_NULL)
    arbitro_fk=models.ForeignKey(Arbitro, null=True, blank=True, on_delete=models.SET_NULL)
    usuario_fk=models.ForeignKey(Usuario, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_inicio=models.DateTimeField()
    fecha_fin=models.DateTimeField()
    subtotal_descuento=models.DecimalField(max_digits=10, decimal_places=2)
    total=models.DecimalField(max_digits=10, decimal_places=2)
    justificacion=models.CharField(max_length=100)
    estado=models.TextField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)