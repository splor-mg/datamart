from django.db import models


class NaturezaReceita(models.Model):
    ano = models.CharField()
    rec_cod = models.CharField()
    rec_desc = models.CharField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'rec_cod'],
                name='unique_ano_rec_cod',
            )
        ]
