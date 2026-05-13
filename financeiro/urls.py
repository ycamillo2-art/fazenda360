from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('relatorios/', views.relatorios, name='relatorios'),
    path('exportar-pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('remover-propriedade/', views.remover_propriedade, name='remover_propriedade'),
    path('remover-categoria/', views.remover_categoria, name='remover_categoria'),
    path('remover-subcategoria/', views.remover_subcategoria, name='remover_subcategoria'),
    path('remover-lancamento/', views.remover_lancamento, name='remover_lancamento'),

]
