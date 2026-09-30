# CampusBite — NIT Jalandhar Canteen Hub

A complete local-first Flask + SQLite web app for NIT Jalandhar students. It unifies Snackers, Nestle, Dominos, Yadav Canteen, Night Canteen and Campus Cafe with menus, occupancy indicators, seat booking, cancellation, a demo admin panel and an explainable traffic predictor.

> The included occupancy history is demo data. Replace it with real check-in/check-out or booking events before production use.

## Run

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000. The SQLite file is created at `data/campusbite.db` on first run. Delete it to reset demo data.

## Stack

Python, Flask, REST-style JSON APIs, SQLite, HTML5, CSS3, vanilla JavaScript, responsive mobile-first UI, scikit-learn LinearRegression, deterministic ML fallback, seeded data, validation, Git-ready structure.

## ML behavior

`ml/traffic_model.py` uses hour, weekday/weekend, meal period, current occupancy and active booking load to predict an occupancy percentage and label it Low, Moderate, High or Very busy. The page shows the contributing reasons and model name. The fallback keeps the app runnable if scikit-learn is not installed.

## Project structure

`app.py` API/server · `db.py` schema/seed/repository · `ml/traffic_model.py` model · `templates/index.html` UI shell · `static/app.js` interactions · `static/styles.css` design system · `static/manus-routes.json` route manifest · `data/` SQLite.

## Demo flow

Choose a canteen, inspect traffic and menu, click Book a seat, select date/time/seats, confirm, then cancel from Upcoming bookings. Admin demo controls update open/closed status and occupied seats.

## Resume bullet

> Built CampusBite, a Flask and SQLite canteen platform for NIT Jalandhar with responsive JavaScript UI, capacity-aware seat booking, REST APIs, seeded persistence, demo admin controls and an explainable scikit-learn occupancy prediction model.
