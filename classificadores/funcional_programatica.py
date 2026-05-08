from django.db import models


class FuncionalProgramatica(models.Model):
    pk = models.CompositePrimaryKey('ano', 'uo_cod', 'acao_cod')
    chave_funcional_programatica = models.CharField()
    ano = models.IntegerField()
    uo_cod = models.IntegerField()
    funcao_cod = models.IntegerField()
    funcao_desc = models.CharField()
    subfuncao_cod = models.IntegerField()
    subfuncao_desc = models.CharField()
    programa_cod = models.IntegerField()
    programa_desc = models.CharField()
    acao_cod = models.IntegerField()
    acao_desc = models.CharField()
