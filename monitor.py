import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://lucynaszymczak.pl/lista-oczekujacych/"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

STATE_FILE = "last_row.json"


# Pobranie strony
response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")


# Znalezienie właściwej tabeli
target_table = None

for table in soup.find_all("table"):
    text = table.get_text(" ", strip=True)

    if "Pozycja" in text and "Imię" in text and "Telefon" in text:
        target_table = table
        break

if target_table is None:
    raise RuntimeError("Nie znaleziono tabeli listy oczekujących.")


# Odczytanie wszystkich wierszy tabeli
rows = []

for row in target_table.find_all("tr"):
    cells = row.find_all("td")

    if len(cells) >= 3:
        rows.append([
            cell.get_text(" ", strip=True)
            for cell in cells[:3]
        ])

if not rows:
    raise RuntimeError("Tabela nie zawiera żadnych pozycji.")


# Aktualny ostatni wiersz
current_row = rows[-1]

print("Aktualny ostatni wiersz:")
print(current_row)


# Odczytanie poprzedniego stanu
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as file:
        previous_row = json.load(file)
else:
    previous_row = None

print("Poprzedni ostatni wiersz:")
print(previous_row)


# Porównanie
if previous_row is not None and previous_row != current_row:

    old_position, old_name, old_phone = previous_row
    new_position, new_name, new_phone = current_row

    message = (
        "🚨 ZMIANA NA LIŚCIE OCZEKUJĄCYCH!\n\n"
        "Poprzedni ostatni wiersz:\n"
        f"{old_position} | {old_name} | {old_phone}\n\n"
        "Obecny ostatni wiersz:\n"
        f"{new_position} | {new_name} | {new_phone}\n\n"
        f"Sprawdź listę:\n{URL}"
    )

    discord_response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )

    discord_response.raise_for_status()

    print("ALERT: ostatni wiersz uległ zmianie. Wiadomość wysłana na Discorda.")

elif previous_row is None:
    print("Pierwsze uruchomienie - zapisuję stan bez wysyłania alertu.")

else:
    print("Brak zmian w ostatnim wierszu.")


# Zapisanie aktualnego stanu
with open(STATE_FILE, "w", encoding="utf-8") as file:
    json.dump(
        current_row,
        file,
        ensure_ascii=False,
        indent=2
    )

print("Zapisano aktualny ostatni wiersz.")
