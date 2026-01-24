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
- `backend/` - backend Django (glowna logika serwera i API)
- `backend/manage.py` - uruchamianie polecen Django
- `backend/requirements.txt` - zaleznosci Pythona
- `backend/backend/` - konfiguracja projektu Django (settings/urls/wsgi)
- `backend/core/` - aplikacja domenowa (modele, serwisy, widoki, migracje)
- `backend/core/rules/scoring.json` - opis lokalnych zasad kompatybilnosci (json)
- `frontend/` - frontend React (Vite)
- `frontend/src/` - widoki, komponenty i serwisy frontendu
- `frontend/package.json` - zaleznosci i skrypty frontendu
- `plans/` - dokumenty planistyczne (np. zasady sortowania/regul)
- `dane/` - dane pomocnicze do projektu
- `info_extractor/` - narzedzia do ekstrakcji danych

## Autor
Projekt inżynierski - Bartosz Bohdziewicz
