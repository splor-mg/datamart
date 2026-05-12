from django.db import models


class FonteRecurso(models.Model):
    chave_fonte_recurso = models.CharField()
    ano = models.IntegerField()
    fonte_cod = models.IntegerField()
    fonte_desc = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'fonte_cod'],
                name='unique_ano_fonte_cod',
            )
        ]
