# CampusBite implementation plan

Browser-rendered Flask frontend plus JSON APIs under `/api/*`, SQLite persistence, seeded demo data, and an explainable occupancy predictor. Static assets live in `/static`; the app runs on port 5000 and exposes `/health` and `/manus-routes.json`. Verification uses Python compilation, health/API smoke tests, and ZIP inspection.
