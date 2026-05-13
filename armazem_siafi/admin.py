from django.contrib import admin

from .alteracao_orcamentaria import AlteracaoOrcamentaria
from .cota import Cota
from .execucao import Execucao
from .execucao_alem_credito import ExecucaoAlemCredito
from .receita import Receita
from .restos_pagar import RestosPagar
from .restos_pagar_folha import RestosPagarFolha


class AlteracaoOrcamentariaAdmin(admin.ModelAdmin):
    pass


class CotaAdmin(admin.ModelAdmin):
    pass


class ExecucaoAdmin(admin.ModelAdmin):
    pass


class ExecucaoAlemCreditoAdmin(admin.ModelAdmin):
    pass


class ReceitaAdmin(admin.ModelAdmin):
    pass


class RestosPagarAdmin(admin.ModelAdmin):
    pass


class RestosPagarFolhaAdmin(admin.ModelAdmin):
    pass


admin.site.register(AlteracaoOrcamentaria, AlteracaoOrcamentariaAdmin)
admin.site.register(Cota, CotaAdmin)
admin.site.register(Execucao, ExecucaoAdmin)
admin.site.register(ExecucaoAlemCredito, ExecucaoAlemCreditoAdmin)
admin.site.register(Receita, ReceitaAdmin)
admin.site.register(RestosPagar, RestosPagarAdmin)
admin.site.register(RestosPagarFolha, RestosPagarFolhaAdmin)
