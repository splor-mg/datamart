from django.db import models


class RestosPagarFolha(models.Model):
    ano = models.CharField()
    mes_cod = models.CharField()
    ano_rp_folha = models.CharField()
    uo_cod = models.CharField()
    grupo_cod = models.CharField()
    modalidade_cod = models.CharField()
    iag_cod = models.CharField()
    fonte_cod = models.CharField()
    ipu_cod = models.CharField()
    vlr_inscrito_folha = models.FloatField()
    vlr_anulado_folha = models.FloatField()
    vlr_pago_folha = models.FloatField()
    vlr_despesa_liquidada_pagar_folha = models.FloatField()
