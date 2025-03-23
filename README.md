# Menedżer Lodówki

Aplikacja webowa do zarządzania zawartością lodówki, listami zakupów i śledzenia wydatków.

## Funkcje

- Zarządzanie produktami w lodówce
  - Dodawanie, edycja i usuwanie produktów
  - Śledzenie dat ważności
  - Kategoryzacja produktów
  - Śledzenie ilości

- Lista zakupów
  - Tworzenie i zarządzanie listami zakupów
  - Oznaczanie produktów jako zakupione
  - Automatyczne dodawanie do lodówki

- Raporty i statystyki
  - Podsumowanie wydatków
  - Śledzenie zużycia produktów
  - Analiza marnowania żywności
  - Eksport raportów do CSV i PDF

- Zarządzanie kategoriami
  - Tworzenie i edycja kategorii produktów
  - Organizacja produktów w kategorie

## Wymagania

- Python 3.8+
- Django 5.0+
- PostgreSQL (opcjonalnie, domyślnie SQLite)

## Instalacja

1. Sklonuj repozytorium:
```bash
git clone https://github.com/twoj-username/menedzer-lodowki.git
cd menedzer-lodowki
```

2. Utwórz i aktywuj wirtualne środowisko:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

4. Wykonaj migracje:
```bash
python manage.py migrate
```

5. Utwórz superużytkownika:
```bash
python manage.py createsuperuser
```

6. Uruchom serwer deweloperski:
```bash
python manage.py runserver
```

7. Otwórz przeglądarkę i przejdź do `http://127.0.0.1:8000`

## Struktura projektu

```
menedzer-lodowki/
├── fridge_manager/      # Główny projekt Django
├── products/           # Aplikacja do zarządzania produktami
├── shopping_list/      # Aplikacja do zarządzania listami zakupów
├── reports/           # Aplikacja do raportów i statystyk
├── users/             # Aplikacja do zarządzania użytkownikami
├── notifications/     # Aplikacja do powiadomień
├── templates/        # Szablony HTML
├── static/          # Pliki statyczne (CSS, JS, obrazy)
├── media/           # Pliki multimedialne
├── requirements.txt  # Zależności projektu
└── README.md        # Ten plik
```

## Rozwój

1. Utwórz nową gałąź dla swojej funkcjonalności:
```bash
git checkout -b feature/nazwa-funkcjonalnosci
```

2. Wprowadź zmiany i zatwierdź je:
```bash
git add .
git commit -m "Dodano nową funkcjonalność"
```

3. Wypchnij zmiany do repozytorium:
```bash
git push origin feature/nazwa-funkcjonalnosci
```

## Licencja

Ten projekt jest licencjonowany na warunkach licencji MIT - zobacz plik [LICENSE](LICENSE) dla szczegółów. 