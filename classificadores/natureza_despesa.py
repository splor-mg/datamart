from django.db import models


class NaturezaDespesa(models.Model):
    ano = models.IntegerField(primary_key=True)
    grupo_cod = models.IntegerField()
    grupo_desc = models.CharField()
    categoria_cod = models.IntegerField()
    categoria_desc = models.CharField()
