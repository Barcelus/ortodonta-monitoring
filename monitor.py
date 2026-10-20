
import os
import json
import requests
from bs4 import BeautifulSoup

URL = "https://lucynaszymczak.pl/lista-oczekujacych/"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]

TARGET_NAME = "Bartłomiej"
STATE_FILE = "bartlomiej_position.json"

# Pobierz stronę
response = requests.get(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# Znajdź właściwą tabelę
target_table = None

for table in soup.find_all("table"):
    text = table.get_text(" ", strip=True)

    if "Pozycja" in text and "Imię" in text and "Telefon" in text:
        target_table = table
        break

if target_table is None:
    raise RuntimeError("Nie znaleziono tabeli listy oczekujących.")

# Znajdź wiersz Bartłomieja
matches = []

for row in target_table.find_all("tr"):
    cells = row.find_all("td")

    if len(cells) >= 3:
        position = cells[0].get_text(" ", strip=True)
        name = cells[1].get_text(" ", strip=True)

        if name.casefold() == TARGET_NAME.casefold():
            matches.append(position)

if not matches:
    raise RuntimeError(
        f"Nie znaleziono osoby {TARGET_NAME} w tabeli."
    )

if len(matches) > 1:
    raise RuntimeError(
        f"Znaleziono więcej niż jeden wiersz z imieniem {TARGET_NAME}. "
        "Nie można jednoznacznie ustalić pozycji."
    )

current_position = matches[0]

print(f"Osoba: {TARGET_NAME}")
print(f"Aktualna pozycja: {current_position}")

# Odczytaj poprzednią pozycję
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r", encoding="utf-8") as file:
        previous_position = json.load(file)
else:
    previous_position = None

print(f"Poprzednia pozycja: {previous_position}")

# Wyślij alert przy zmianie numeru
if previous_position is not None and previous_position != current_position:

    message = (
        f"🚨 ZMIANA POZYCJI NA LIŚCIE!\n\n"
        f"Osoba: {TARGET_NAME}\n"
        f"Poprzednia pozycja: {previous_position}\n"
        f"Nowa pozycja: {current_position}\n\n"
        f"Sprawdź listę:\n{URL}"
    )

    discord_response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )
    discord_response.raise_for_status()

    print("ALERT: wysłano powiadomienie na Discord.")

elif previous_position is None:
    print("Pierwsze uruchomienie: zapisuję pozycję bez alertu.")

else:
    print("Pozycja bez zmian.")

# Zapisz aktualną pozycję
with open(STATE_FILE, "w", encoding="utf-8") as file:
    json.dump(
        current_position,
        file,
        ensure_ascii=False,
        indent=2
    )

print(f"Zapisano pozycję: {current_position}")
