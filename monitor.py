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

# Znajdź tabelę listy oczekujących
target_table = None

for table in soup.find_all("table"):
    text = table.get_text(" ", strip=True)
    if "Pozycja" in text and "Imię" in text and "Telefon" in text:
        target_table = table
        break

if target_table is None:
    raise RuntimeError("Nie znaleziono tabeli listy oczekujących.")

# Pobierz wszystkie wiersze z danymi
rows = []

for row in target_table.find_all("tr"):
    cells = row.find_all("td")

    if len(cells) >= 3:
        values = [
            cell.get_text(" ", strip=True)
            for cell in cells[:3]
        ]
        rows.append(values)

if not rows:
    raise RuntimeError("Tabela nie zawiera żadnych pozycji.")

# Ostatni wiersz tabeli
last_row = rows[-1]

position, name, phone = last_row

print("Aktualny ostatni wpis:")
print(f"Pozycja: {position}")
print(f"Imię: {name}")
print(f"Telefon: {phone}")

# Sprawdź, czy pozycja 30 nadal istnieje
if position == "30":
    print("STATUS: Pozycja 30 nadal zajęta.")
else:
    print("STATUS: ZWOLNIŁO SIĘ MIEJSCE!")
