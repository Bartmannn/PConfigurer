# PC Configurator 🖥️

Projekt inżynierski: aplikacja do konfiguracji zestawów komputerowych.  
Backend oparty na **Django** + **Django REST Framework**, frontend planowany w **React**.

## Funkcje (na start)
- Modele dla podzespołów komputerowych (CPU, GPU, RAM, płyta główna, itp.).
- Modele użytkowników i ich zestawów (Builds).
- API REST do zarządzania częściami i zestawami.
- Panel admina do wprowadzania danych.
- Możliwość sprawdzenia kompatybilności (w planach).
- Kalkulacja bottleneck / FPS (w planach).

---

## Technologie
- Python 3.10+
- Django 5.x
- Django REST Framework
- SQLite (domyślnie) lub PostgreSQL (zalecane)

---

## Instalacja i uruchomienie

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/Bartmannn/PConfigurer.git
cd pc-configurator
```

### 2. Wirtualne środowisko
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

### 3. Instalacja zależności
pip install -r requirements.txt

### 4. Migracje bazy
python manage.py makemigrations
python manage.py migrate

### 5. Utworzenie konta administratora
python manage.py createsuperuser

### 6. Uruchomienie serwera
python manage.py runserver

## API (przykłady)
- GET /api/cpus/ → lista procesorów
- GET /api/gpus/ → lista kart graficznych
- POST /api/builds/ → utworzenie nowego zestawu
- GET /admin/ → panel administratora

## Autor
Projekt inżynierski - Bartosz Bohdziewicz