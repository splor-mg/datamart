from django.db import models


class NaturezaReceita(models.Model):
    pk = models.CompositePrimaryKey('ano', 'rec_cod')
    chave_natureza_receita = models.CharField()
    ano = models.IntegerField()
    rec_cod = models.IntegerField()
    rec_desc = models.CharField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['ano', 'rec_cod'],
                name='unique_ano_rec_cod',
            )
        ]
