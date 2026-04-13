# CVMatch-AI

## PFE CV Analyzer (React + FastAPI + Ollama)

Architecture orientée **Clean Architecture** avec frontend React et backend FastAPI.

## Structure

- `frontend/src/` : frontend (UI + appels Axios)
- `frontend/src/lib/axios.ts` : client Axios central + intercepteurs
- `backend/app/` : backend modulaire (`api`, `application`, `domain`, `infrastructure`, `core`)
- `backend/tests/smoke_runner.py` : mini runner de vérification du scoring
- `backend/tests/smoke_upload_runner.py` : vérification parsing upload docx
- `backend/tests/smoke_ingestion_job_runner.py` : vérification persistance des jobs d'ingestion

## Prérequis

- Node.js 20+
- Python 3.11+
- Ollama local (optionnel mais recommandé)

## Démarrage rapide

### Option pratique (depuis la racine du repo)

```bash
npm run frontend:install
npm run frontend:dev
```

Pour builder le frontend depuis la racine:

```bash
npm run frontend:build
```

### 1) Installer les dépendances frontend

```bash
cd frontend
npm install
```

### 2) Installer les dépendances backend

```bash
cd backend
python -m pip install -r requirements.txt
```

### 3) Lancer l'API FastAPI

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 4) Lancer le frontend

```bash
cd frontend
npm run dev
```

## Endpoints principaux

- `GET /api/v1/health`
- `POST /api/v1/score`
- `GET /api/v1/dashboard/stats`
- `POST /api/v1/jobs/`
- `POST /api/v1/cvs/upload`
- `GET /api/v1/cvs/ingestion-jobs/{job_id}`
- `GET /api/v1/candidates/`
- `GET /api/v1/analytics/`
- `GET|PUT /api/v1/parameters/scoring`

## Smoke test backend

```bash
cd backend
python -m tests.smoke_runner
python -m tests.smoke_upload_runner
python -m tests.smoke_ingestion_job_runner
```
