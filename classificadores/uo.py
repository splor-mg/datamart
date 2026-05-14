from django.db import models


class UnidadeOrcamentaria(models.Model):
    ano = models.CharField()
    orgao_vinculacao_cod = models.CharField()
    orgao_vinculacao_nome = models.CharField()
    poder_cod = models.CharField()
    poder_desc = models.CharField()
    uo_cod = models.CharField()
    uo_nome = models.CharField()
    uo_sigla = models.CharField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'uo_cod'],
                name='unique_ano_uo_cod',
            )
        ]
