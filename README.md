# PC Configurator 🖥️

Projekt inzynierski: aplikacja do konfiguracji zestawow komputerowych.  
Backend: **Django** + **Django REST Framework**, frontend: **React** (Vite).

## Funkcje
- Modele dla podzespolow komputerowych (CPU, GPU, RAM, plyta glowna, itp.).
- Zestawy (Builds) oraz REST API do zarzadzania danymi.
- Panel admina do wprowadzania danych.
- Widok szczegolow z lokalnymi uwagami kompatybilnosci.
- Listy podzespolow sortowane po kompatybilnosci i cenie.

---

## Technologie
- Python 3.10+
- Django 5.x
- Django REST Framework
- SQLite (domyślnie) lub PostgreSQL (zalecane)
- React 19 + Vite

---

## Instalacja i uruchomienie

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/Bartmannn/PConfigurer.git
cd PConfigurer
```

### 2. Backend (Django)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 3. Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

## API (przykłady)
- GET /api/cpus/ -> lista procesorow
- GET /api/gpus/ -> lista kart graficznych
- GET /api/filters/options/ -> dane do filtrow
- POST /api/builds/ -> utworzenie nowego zestawu
- GET /admin/ -> panel administratora

## Struktura projektu
```
PConfigurer/
|-- backend/                            -- warstwa serwerowa
|   |-- backend/                        -- konfiguracja projektu Django
|   |-- core/                           -- logika aplikacji
|   |   |-- filterset.py                -- definicje filtrow
|   |   |-- fixtures/                   -- dane testowe
|   |   |-- migrations/                 -- migracje bazy danych
|   |   |-- models.py                   -- modele danych
|   |   |-- serializer.py               -- serializacja modeli
|   |   |-- services/                   -- uslugi domenowe
|   |   |-- tools.py                    -- funkcje pomocnicze
|   |   `-- views.py                    -- widoki API
|   |-- db.sqlite3                      -- lokalna baza testowa
|   |-- manage.py                       -- narzedzia zarzadzania
|   `-- requirements.txt                -- wymagane moduly Pythona
`-- frontend/                           -- warstwa kliencka
    |-- public/                         -- pliki statyczne
    `-- src/                            -- zrodla aplikacji React
        |-- assets/                     -- zasoby graficzne
        |-- context/                    -- konteksty aplikacji
        |   `-- ConfiguratorContext.jsx -- kontekst konfiguratora
        |-- pages/                      -- widoki stron
        |   `-- Configurator.jsx        -- strona konfiguratora
        |-- services/                   -- uslugi API
        |   |-- BuildEvaluationService.js -- ocena konfiguracji
        |   `-- remarksService.js       -- uwagi i komentarze
        `-- vertical-components/        -- komponenty ukladu
            |-- BuildEvaluation.jsx     -- widok oceny
            |-- ComponentDetails.jsx    -- szczegoly komponentu
            |-- ComponentList.jsx       -- lista komponentow
            |-- ConfiguratorLayout.jsx  -- uklad konfiguratora
            |-- FiltersPanel.jsx        -- panel filtrow
            |-- SelectView.jsx          -- widok wyboru
            `-- SummaryView.jsx         -- widok podsumowania
```

## Autor
Projekt inżynierski - Bartosz Bohdziewicz
