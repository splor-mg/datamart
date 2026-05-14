from django.db import models


class FonteRecurso(models.Model):
    ano = models.CharField()
    fonte_cod = models.CharField()
    fonte_desc = models.CharField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'fonte_cod'],
                name='unique_ano_fonte_cod',
            )
        ]
