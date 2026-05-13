from django.contrib import admin
from .acao import Acao
from .elemento_item import ElementoItem
from .fonte_recurso import FonteRecurso
from .funcional_programatica import FuncionalProgramatica
from .natureza_despesa import NaturezaDespesa
from .natureza_receita import NaturezaReceita
from .uo import UnidadeOrcamentaria


class AcaoAdmin(admin.ModelAdmin):
    pass

class ElementoItemAdmin(admin.ModelAdmin):
    pass

class FonteRecursoAdmin(admin.ModelAdmin):
    pass

class FuncionalProgramaticaAdmin(admin.ModelAdmin):
    pass

class NaturezaDespesaAdmin(admin.ModelAdmin):
    pass

class NaturezaReceitaAdmin(admin.ModelAdmin):
    pass

class UnidadeOrcamentariaAdmin(admin.ModelAdmin):
    pass


admin.site.register(Acao, AcaoAdmin)
admin.site.register(ElementoItem, ElementoItemAdmin)
admin.site.register(FonteRecurso, FonteRecursoAdmin)
admin.site.register(FuncionalProgramatica, FuncionalProgramaticaAdmin)
admin.site.register(NaturezaDespesa, NaturezaDespesaAdmin)
admin.site.register(NaturezaReceita, NaturezaReceitaAdmin)
admin.site.register(UnidadeOrcamentaria, UnidadeOrcamentariaAdmin)
