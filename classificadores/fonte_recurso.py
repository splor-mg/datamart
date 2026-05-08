from django.db import models


class FonteRecurso(models.Model):
    pk = models.CompositePrimaryKey('ano', 'fonte_cod')
    chave_fonte_recurso = models.CharField()
    ano = models.IntegerField()
    fonte_cod = models.IntegerField()
    fonte_desc = models.IntegerField()
