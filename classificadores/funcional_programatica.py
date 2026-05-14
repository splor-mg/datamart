from django.db import models


class FuncionalProgramatica(models.Model):
    ano = models.CharField()
    uo_cod = models.CharField()
    funcao_cod = models.CharField()
    funcao_desc = models.CharField()
    subfuncao_cod = models.CharField()
    subfuncao_desc = models.CharField()
    programa_cod = models.CharField()
    programa_desc = models.CharField()
    acao_cod = models.CharField()
    acao_desc = models.CharField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'uo_cod', 'acao_cod'],
                name='unique_ano_uo_acao_cod',
            )
        ]
