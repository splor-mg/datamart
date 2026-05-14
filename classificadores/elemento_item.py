from django.db import models


class ElementoItem(models.Model):
    ano = models.CharField()
    elemento_item_cod = models.CharField()
    elemento_item_desc = models.CharField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["ano", "elemento_item_cod"],
                name="unique_ano_elemento_item_cod",
            )
        ]
