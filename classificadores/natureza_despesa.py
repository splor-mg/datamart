from django.db import models


class NaturezaDespesa(models.Model):
    ano = models.CharField(primary_key=True)
    grupo_cod = models.CharField()
    grupo_desc = models.CharField()
    categoria_cod = models.CharField()
    categoria_desc = models.CharField()
