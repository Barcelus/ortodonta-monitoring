import requests
from bs4 import BeautifulSoup

URL = "https://lucynaszymczak.pl/lista-oczekujacych/"

response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Znajdź tabelę zawierającą nagłówki:
# Pozycja | Imię | Telefon
target_table = None

for table in soup.find_all("table"):
    text = table.get_text(" ", strip=True)
    if "Pozycja" in text and "Imię" in text and "Telefon" in text:
        target_table = table
        break

if target_table is None:
    raise RuntimeError("Nie znaleziono tabeli listy oczekujących.")

rows = target_table.find_all("tr")

data_rows = []
for row in rows:
    cells = row.find_all("td")
    if len(cells) >= 3:
        data_rows.append([
            cell.get_text(" ", strip=True)
            for cell in cells[:3]
        ])

if not data_rows:
    raise RuntimeError("Tabela nie zawiera żadnych pozycji.")

last_row = data_rows[-1]

position, name, phone = last_row

print("Ostatnia pozycja na liście:")
print(f"Pozycja: {position}")
print(f"Imię: {name}")
print(f"Telefon: {phone}")
