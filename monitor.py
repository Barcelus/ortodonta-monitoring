import os
import requests
from bs4 import BeautifulSoup

URL = "https://lucynaszymczak.pl/lista-oczekujacych/"
DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


# Pobierz stronę
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


# Pobierz wiersze tabeli
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


# Ostatni wpis
position, name, phone = rows[-1]

print("Aktualny ostatni wpis:")
print(f"Pozycja: {position}")
print(f"Imię: {name}")
print(f"Telefon: {phone}")


# TEST — wyślij wiadomość do Discorda
message = (
    "TEST — monitor ortodontyczny działa.\n\n"
    f"Aktualny ostatni wpis: {position} | {name} | {phone}"
)

discord_response = requests.post(
    DISCORD_WEBHOOK_URL,
    json={"content": message},
    timeout=30
)

discord_response.raise_for_status()

print("Wiadomość została wysłana do Discorda.")
