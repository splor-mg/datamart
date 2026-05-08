from django.db import models


class ElementoItem(models.Model):
    pk = models.CompositePrimaryKey('ano', 'elemento_item_cod')
    chave_elemento_item = models.CharField()
    ano = models.IntegerField()
    elemento_item_cod = models.IntegerField()
    elemento_item_desc = models.CharField()
