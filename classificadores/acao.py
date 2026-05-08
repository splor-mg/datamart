from django.db import models


class Acao(models.Model):
    pk = models.CompositePrimaryKey('ano', 'acao_cod')
    chave_acao = models.CharField()
    ano = models.IntegerField()
    acao_cod = models.IntegerField()
    acao_desc = models.CharField()
