# 🎯 PFE-CV-Scoring — Analyse de CV et Scoring Automatique par IA (CVMatch-AI)

Un système moderne d'évaluation de CV basé sur l'Intelligence Artificielle. Conçu pour le Projet de Fin d'Études (PFE) 2024-2025/2026, ce système analyse, extrait et score des profils de candidats en local par rapport à des fiches de poste avec une Architecture orientée **Clean Architecture**.

---

## 🧠 État de l'Art 2025–2026 : Pipeline d'Analyse de CV par IA

Ce projet implémente les méthodes les plus récentes en matière d'analyse documentaire et de NLP, remplaçant les approches classiques (Regex purs, spaCy NER, Cosinus simple) par un pipeline SOTA (State of the Art).

### 1. Parsing de Documents (PDF/DOCX → Texte Structuré)

Le parsing de documents a connu une **révolution complète** entre 2024 et 2026. L'ancienne approche consistait à extraire du texte brut ligne par ligne. Aujourd'hui, les modèles de **Document Intelligence** comprennent visuellement la mise en page comme un humain le ferait.

Dans ce projet, nous utilisons :
*   **Docling 2.x** : Utilisé comme parser principal. Il détecte automatiquement les colonnes, tableaux et hiérarchies visuelles pour générer un Markdown structuré parfait pour les LLMs.
*   **pymupdf4llm** : Utilisé comme solution de fallback rapide ("fallback léger").

### 2. Moteur NLP & Extraction (Structured Output)

L'extraction d'information a été complètement transformée par les **Structured Outputs** des LLMs. En 2026, la méthode standard est désormais : LLM + Schéma forcé + Validation.
*   **Instructor + Ollama (Modèle local Qwen3-8B)** : Le LLM est contraint par un schéma valide strictly typé (`Pydantic`). Il ne peut pas "halluciner" de structure, garantissant un JSON de sortie 100% robuste.
*   **Couches hybrides** : Un pré-traitement Regex (emails, numéros) allège le travail du LLM, suivi d'une validation forte Pydantic.

### 3. Représentation Vectorielle (Advanced Embeddings)

Nous utilisons la référence actuelle du benchmark MTEB pour la sémantique :
*   **BAAI/bge-m3** : Remplace les anciens modèles (MiniLM). Il gère 8192 tokens et est multilingue.
*   **ColBERT (Late Interaction)** : Au lieu d'un seul vecteur global, le modèle génère des embeddings au niveau des tokens. Cela permet un matching de précision "mot-pour-mot/compétence-par-compétence".

### 4. Moteur de Scoring (Architecture 3 Étapes : Retrieve → Rerank → Reason)

Le score de pertinence n'est plus un simple produit scalaire. Il suit l'architecture moderne des systèmes RAG évolués :
1.  **Retrieve (Bi-Encoder)** : Filtrage rapide via similarité cosinus segmentée (skills séparés de l'expérience) avec bge-m3.
2.  **Rerank (Cross-Encoder)** : Re-classement ultra-précis avec `bge-reranker-v2.5-gemma2-lightweight` qui analyse conjointement le profil cible et le profil candidat.
3.  **Reason (LLM-as-a-Judge)** : Qwen3-8B analyse le match final et génère un objet structuré expliquant précisément au recruteur les "Gaps" (lacunes), les forces, et recommandant une action.

### Synthèse de la Stack IA Locale 
| Composant | Technologie 2025/2026 | Rôle |
| :--- | :--- | :--- |
| **Parsing** | Docling 2.x | Compréhension du Layout PDF → Markdown |
| **Extraction** | Instructor + Qwen3:8B | Markdown → Profil JSON Validé Pydantic |
| **Embeddings** | BAAI/bge-m3 | Textes → Vecteurs Denses & ColBERT |
| **Reranking** | bge-reranker-v2.5 | Re-classement précis Candidat/Job |
| **Explicabilité** | LLM-as-a-Judge | Génération du Feedback Recruteur |
| **Inférence** | Ollama | Execution CPU/GPU locale des LLMs |

---

## 💻 Frontend (React + Vite)

A modern, single-page CV analysis and AI scoring dashboard built with **React**, **TypeScript**, **Vite**, and **Tailwind CSS**. This frontend application connects to a FastAPI backend to score candidates and provide rich analytics and filtering tools for recruiters.

### Live Tech Stack

| Category            | Technology             | Purpose                                                        |
| ------------------- | ---------------------- | -------------------------------------------------------------- |
| **Framework**       | React 19.2.3           | UI library (components, state, effects)                        |
| **Language**        | TypeScript 5.9.3       | Type safety and developer experience                           |
| **Bundler**         | Vite 7.2.4             | Fast development server and optimized production builds        |
| **Styling**         | Tailwind CSS 4.1.17    | Utility-first CSS framework                                    |
| **Charts**          | Recharts 3.8.1         | Interactive data visualizations (analytics)                    |
| **HTTP Client**     | Axios 1.14.0           | REST API communication with backend                            |

The codebase follows a **feature-based modular architecture** with clear separation of concerns (Containers / Presentational split, Custom Hooks for Business Logic, Centralized Type Definitions).

---

## ⚙️ Backend (FastAPI + PostgreSQL)

API REST asynchrone et robuste propulsant le pipeline NLP pour le matching.

### Architecture
- `backend/app/api` : Contrôleurs REST
- `backend/app/core` : Logique IA / NLP (parse, extract, embeddings, scoring)
- `backend/app/models` : Entités SQLAlchemy

### Technologies / Infrastructure Backend
- **Framework** : FastAPI 
- **Base de Données** : PostgreSQL 15 couplé avec **`pgvector`** (SQLAlchemy + Alembic).
- **Vector Store** : ChromaDB (optionnel pour RAG persistant).

---

## 🚀 Démarrage Rapide

### Prérequis
- Node.js 20+
- Python 3.11+
- Optionnel : Docker & Docker Compose (pour PostgreSQL + pgvector)
- Au moins 8 Go de RAM (pour exécuter l'inférence via Ollama)

### Option 1 : Déploiement complet via Docker Compose (Recommandé)

Docker orchestrera PostgreSQL, ChromaDB, FastAPI, et le Frontend.

```bash
# Lancement de l'infrastructure
docker-compose up -d --build

# Initialisation de la BDD (migrations Alembic)
docker exec -it cv_scoring_db alembic upgrade head
```

### Option 2 : Exécution Locale (Dev Mode)

#### 1. Lancer l'infrastructure (DB uniquement)
```bash
docker compose up -d postgres
```

#### 2. Démarrer le Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Initialiser la base de données
alembic upgrade head

# Lancer FastAPI
uvicorn app.main:app --reload --port 8000
```

#### 3. Démarrer le Frontend
```bash
cd frontend
npm install
npm run dev
```

## Endpoints principaux (API)

- `GET /api/v1/health`
- `POST /api/v1/jobs/`
- `POST /api/v1/jobs/{job_id}/cvs/upload`
- `GET /api/v1/jobs/{job_id}/scores`
- `GET /api/v1/cvs/{cv_id}/score`

---
*Projet de Fin d'Études — Année Universitaire 2025/2026*
