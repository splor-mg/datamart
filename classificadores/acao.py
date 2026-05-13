from django.db import models


class Acao(models.Model):
    chave_acao = models.CharField()
    ano = models.IntegerField()
    acao_cod = models.IntegerField()
    acao_desc = models.CharField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'acao_cod'],
                name='unique_ano_acao_cod',
            )
        ]
