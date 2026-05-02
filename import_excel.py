import pandas as pd
import os
import django

# Configuração do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fazenda360.settings')
django.setup()

from financeiro.models import Propriedade, Categoria, Subcategoria, Tipo, Lancamento

def limpar_texto(texto):
    if pd.isna(texto): return ""
    # Tratar encoding comum de Excel/VBA
    try:
        t = str(texto).encode('latin1').decode('utf-8')
    except:
        t = str(texto)
    return t.strip()

def limpar_valor(valor):
    if pd.isna(valor): return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    # Se for string, limpar TUDO que não for número ou vírgula/ponto
    s = str(valor).upper().replace('R$', '').replace('RR$', '').strip()
    
    # Se tiver ponto E vírgula (ex: 1.234,56)
    if '.' in s and ',' in s:
        s = s.replace('.', '').replace(',', '.')
    # Se tiver apenas vírgula (ex: 1234,56)
    elif ',' in s:
        s = s.replace(',', '.')
    
    try:
        return float(s)
    except:
        return 0.0

def importar_excel(caminho_arquivo):
    print(f"Iniciando importação de: {caminho_arquivo}")
    
    try:
        df = pd.read_excel(caminho_arquivo, sheet_name='BD')
        
        # Mapeamento manual baseado na estrutura real da planilha
        # A planilha tem: DATA, PROPRIEDADE, CATEGORIA, SUBCATEGORIA, TIPO, DESCRIÇÃO, VALOR
        
        count_sucesso = 0
        
        # Limpar o banco antes de re-importar para evitar duplicidade e lixo
        Lancamento.objects.all().delete()
        Subcategoria.objects.all().delete()
        Categoria.objects.all().delete()
        Propriedade.objects.all().delete()
        Tipo.objects.all().delete()

        for index, row in df.iterrows():
            try:
                # Pegar colunas por posição para evitar erros de encoding nos nomes das colunas
                # 0: Data, 1: Propriedade, 2: Categoria, 3: Subcategoria, 4: Tipo, 5: Descrição, 6: Valor
                data = row.iloc[0]
                if pd.isna(data): continue
                
                prop_nome = limpar_texto(row.iloc[1])
                cat_nome = limpar_texto(row.iloc[2])
                sub_nome = limpar_texto(row.iloc[3])
                tipo_nome = limpar_texto(row.iloc[4])
                desc = limpar_texto(row.iloc[5])
                valor = limpar_valor(row.iloc[6])

                if not prop_nome or valor == 0: continue

                prop, _ = Propriedade.objects.get_or_create(nome=prop_nome)
                cat, _ = Categoria.objects.get_or_create(nome=cat_nome)
                sub, _ = Subcategoria.objects.get_or_create(nome=sub_nome, categoria=cat)
                tipo, _ = Tipo.objects.get_or_create(nome=tipo_nome)
                
                Lancamento.objects.create(
                    data=data,
                    propriedade=prop,
                    categoria=cat,
                    subcategoria=sub,
                    tipo=tipo,
                    valor=valor,
                    descricao=desc
                )
                count_sucesso += 1
            except Exception as e:
                pass # Silencioso para não poluir, mas pode-se logar se necessário
                
        print(f"Importação concluída! Total: {count_sucesso}")
        
    except Exception as e:
        print(f"Erro ao ler arquivo: {e}")

if __name__ == "__main__":
    # Exemplo de uso
    # importar_excel('dados_legado.xlsx')
    print("Para importar, execute: python import_excel.py <caminho_do_arquivo>")
