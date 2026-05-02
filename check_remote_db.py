import os
import django

os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from financeiro.models import Lancamento, Propriedade

print(f"Total de Propriedades no Postgres: {Propriedade.objects.count()}")
print(f"Total de Lançamentos no Postgres: {Lancamento.objects.count()}")

if Lancamento.objects.count() > 0:
    first = Lancamento.objects.first()
    print(f"Exemplo de lançamento: {first.descricao} - {first.valor}")
