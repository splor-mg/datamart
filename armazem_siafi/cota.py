from django.db import models


class Cota(models.Model):
    ano = models.CharField()
    poder_cod = models.CharField()
    uo_cod = models.CharField()
    ue_cod = models.CharField()
    acao_cod = models.CharField()
    grupo_cod = models.CharField()
    modalidade_cod = models.CharField()
    iag_cod = models.CharField()
    fonte_cod = models.CharField()
    ipu_cod = models.CharField()
    elemento_item_cod = models.CharField()
    data_registro_cota = models.DateTimeField()
    operador_registro = models.CharField()
    operador_cancelamento = models.CharField()
    documento_aprovacao_cota = models.CharField()
    vlr_cota_aprovada = models.FloatField()
    vlr_cota_cancelada = models.FloatField()
    vlr_cota_anulada = models.FloatField()
    vlr_cota_aprovada_liquida = models.FloatField()
