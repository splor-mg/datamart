from django.db import models


class UnidadeOrcamentaria(models.Model):
    pk = models.CompositePrimaryKey('ano', 'uo_cod')
    chave_uo = models.CharField()
    ano = models.IntegerField()
    orgao_vinculacao_cod = models.IntegerField()
    orgao_vinculacao_nome = models.CharField()
    poder_cod = models.IntegerField()
    poder_desc = models.CharField()
    uo_cod = models.IntegerField()
    uo_nome = models.CharField()
    uo_sigla = models.CharField()
    uo_sigla_current = models.CharField()
