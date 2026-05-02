import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from financeiro.models import Propriedade, Categoria, Subcategoria, Tipo, Lancamento

def limpar_banco():
    print("Limpando dados antigos...")
    Lancamento.objects.all().delete()
    Subcategoria.objects.all().delete()
    Categoria.objects.all().delete()
    Propriedade.objects.all().delete()
    Tipo.objects.all().delete()
    print("Banco de dados limpo com sucesso!")

if __name__ == "__main__":
    limpar_banco()
