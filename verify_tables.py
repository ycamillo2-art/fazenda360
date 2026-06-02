import os
import django
import dj_database_url

os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from django.db import connection

tables = connection.introspection.table_names()
print(f"Tables found in DB: {len(tables)}")
for table in sorted(tables):
    print(f" - {table}")
