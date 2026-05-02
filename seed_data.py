import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from financeiro.models import Propriedade, Categoria, Subcategoria, Tipo
from django.contrib.auth.models import User

# Criar Superusuário
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fazenda360.com', 'admin123')
    print("Superusuário 'admin' criado (senha: admin123)")

# Criar Dados Iniciais
props = ['Fazenda Boa Vista', 'Sítio Recanto']
for p in props:
    Propriedade.objects.get_or_create(nome=p)

tipos = ['Entrada', 'Saída', 'Investimento']
for t in tipos:
    Tipo.objects.get_or_create(nome=t)

cats = {
    'Produção': ['Sementes', 'Fertilizantes', 'Mão de Obra'],
    'Vendas': ['Soja', 'Milho', 'Gado'],
    'Administrativo': ['Energia', 'Internet', 'Impostos']
}

for cat_nome, subs in cats.items():
    c, _ = Categoria.objects.get_or_create(nome=cat_nome)
    for s_nome in subs:
        Subcategoria.objects.get_or_create(nome=s_nome, categoria=c)

print("Dados de exemplo carregados com sucesso!")
