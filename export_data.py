import os
import json
import django
from django.core import serializers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from financeiro.models import Propriedade, Categoria, Subcategoria, Tipo, Lancamento

# Export all financeiro models
models = [Propriedade, Categoria, Subcategoria, Tipo, Lancamento]
data = []

for model in models:
    objects = model.objects.all()
    data.extend(json.loads(serializers.serialize('json', objects)))

with open('data_dump_utf8.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Exportado com sucesso para data_dump_utf8.json")
