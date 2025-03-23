# Menedżer Lodówki

Aplikacja do zarządzania zawartością lodówki, która pozwala użytkownikom na monitorowanie produktów, sprawdzanie dat ważności, tworzenie listy zakupów oraz zarządzanie zużyciem produktów.

## Funkcjonalności

- Monitorowanie zawartości lodówki
- Powiadomienia o dacie ważności produktów
- Tworzenie i zarządzanie listą zakupów
- Sprawdzanie zużycia produktów
- Rejestracja i logowanie użytkowników
- Zarządzanie kontem użytkownika

## Wymagania

- Python 3.10+
- PostgreSQL
- Node.js i npm (dla Tailwind CSS)

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/twoj-username/fridge-manager.git
cd fridge-manager
```

2. Utwórz i aktywuj środowisko wirtualne:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Zainstaluj zależności Python:
```bash
pip install -r requirements.txt
```

4. Zainstaluj zależności Node.js:
```bash
npm install
```

5. Skonfiguruj bazę danych PostgreSQL:
- Utwórz bazę danych o nazwie `fridge_manager_db`
- Zaktualizuj ustawienia w pliku `fridge_manager/settings.py` jeśli potrzebujesz zmienić dane dostępowe do bazy

6. Wykonaj migracje:
```bash
python manage.py migrate
```

7. Utwórz superużytkownika:
```bash
python manage.py createsuperuser
```

## Uruchomienie

1. Uruchom serwer deweloperski:
```bash
python manage.py runserver
```

2. Otwórz przeglądarkę i przejdź do:
```
http://localhost:8000
```

## Rozwój

1. Kompilacja Tailwind CSS:
```bash
npm run build
```

2. Uruchomienie testów:
```bash
python manage.py test
```

## Licencja

MIT 