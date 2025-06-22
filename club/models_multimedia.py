from django.db import models


class Multimedia(models.Model):
    TIPO_CHOICES = [
        ("foto", "Foto"),
        ("video", "Video"),
    ]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=100)
    archivo = models.FileField(upload_to="multimedia/")
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    publicado = models.BooleanField(default=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.tipo})"


class Testimonio(models.Model):
    nombre = models.CharField(max_length=100)
    texto = models.TextField()
    foto = models.ImageField(upload_to="testimonios/", blank=True, null=True)
    fecha = models.DateField(auto_now_add=True)
    publicado = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.fecha})"
