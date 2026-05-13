from django.db import models


class ExecucaoAlemCredito(models.Model):
    ano = models.CharField()
    mes_cod = models.CharField()
    mes_regularizacao = models.CharField()
    mes_registro = models.CharField()
    uo_cod = models.CharField()
    funcao_cod = models.CharField()
    acao_cod = models.CharField()
    grupo_cod = models.CharField()
    modalidade_cod = models.CharField()
    iag_cod = models.CharField()
    fonte_cod = models.CharField()
    ipu_cod = models.CharField()
    elemento_item_cod = models.CharField()
    vlr_alem_credito = models.FloatField()
    vlr_regularizado = models.FloatField()
    vlr_anulado = models.FloatField()
