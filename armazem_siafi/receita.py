from django.db import models


class Receita(models.Model):
    ano = models.CharField()
    mes_cod = models.CharField()
    uo_cod = models.CharField()
    fonte_cod = models.CharField()
    receita_cod = models.CharField()
    receita_cod_formatado = models.CharField()
    vlr_previsto_inicial = models.FloatField()
    vlr_previsto_adicional = models.FloatField()
    vlr_previsto_atualizado = models.FloatField()
    vlr_contabilizado = models.FloatField()
    vlr_efetivado_ajustado = models.FloatField()
