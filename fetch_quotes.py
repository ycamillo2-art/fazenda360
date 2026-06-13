import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def fetch_quotes():
    url = "https://cooabriel.coop.br/cotacao-do-dia/"
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Encontrar a tabela ou os elementos de cotação
            # No site da Cooabriel, os dados estão em uma tabela
            table = soup.find('table')
            quotes = {}
            if table:
                rows = table.find_all('tr')
                for row in rows[1:]: # Pular cabeçalho
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        tipo = cols[0].text.strip()
                        preco = cols[3].text.strip()
                        if "Conilon 7" in tipo or "Conilon 8" in tipo:
                            quotes[tipo] = preco
            
            if quotes:
                data = {
                    "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "quotes": quotes
                }
                # Salvar em um arquivo JSON que o Django possa ler
                with open('coffee_quotes.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print("Cotações atualizadas com sucesso.")
            else:
                print("Nenhuma cotação encontrada.")
    except Exception as e:
        print(f"Erro ao buscar cotações: {e}")

if __name__ == "__main__":
    fetch_quotes()
