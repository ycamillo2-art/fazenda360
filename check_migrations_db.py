import os
import django

os.environ['DATABASE_URL'] = 'postgresql://admin:9juLiOSs7SKwQHms04OmXPGO8xOCidY3@dpg-d7r77b1j2pic73f5t5i0-a.virginia-postgres.render.com/fazenda360'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY applied DESC LIMIT 5")
    rows = cursor.fetchall()
    print("Recent migrations applied:")
    for row in rows:
        print(f" - {row[0]}: {row[1]} (Applied at: {row[2]})")
