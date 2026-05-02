from django.contrib import admin
from .models import Propriedade, Categoria, Subcategoria, Tipo, Lancamento

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria')
    list_filter = ('categoria',)

@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Lancamento)
class LancamentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'propriedade', 'categoria', 'tipo', 'valor')
    list_filter = ('propriedade', 'categoria', 'tipo', 'data')
    date_hierarchy = 'data'
