import os
import django

os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from django.core import management
with open('backup_dados_reais.json', 'w', encoding='utf-8') as f:
    management.call_command('dumpdata', 'financeiro', stdout=f)
print("Backup concluído com sucesso!")
