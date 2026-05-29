# InkNotes - Blog App

A clean blog application built with FastAPI, PostgreSQL, Docker, and vanilla HTML/CSS/JS.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | FastAPI + SQLAlchemy |
| Database | PostgreSQL 16 |
| Frontend | HTML / CSS / Vanilla JS |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions + GHCR + Trivy |
| Deployment | Kubernetes manifests, AWS/EKS left for you |

## Project Structure

```text
blog-app/
|-- .github/workflows/ci-cd.yml
|-- backend/
|   |-- main.py
|   |-- models.py
|   |-- schemas.py
|   |-- database.py
|   |-- test_main.py
|   |-- requirements.txt
|   `-- Dockerfile
|-- frontend/
|   |-- index.html
|   |-- nginx.conf
|   `-- Dockerfile
|-- k8s/
|   |-- namespace.yaml
|   |-- postgres.yaml
|   |-- backend.yaml
|   |-- frontend.yaml
|   `-- ingress-placeholder.yaml
|-- docs/
|   `-- ci-cd-github-actions.md
`-- docker-compose.yml
```

## Run Locally

```bash
docker compose up --build
```

- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

The frontend calls the backend through `/api` using the Nginx reverse proxy in `frontend/nginx.conf`.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Health check |
| GET | `/posts` | List all posts |
| GET | `/posts/{id}` | Get post by ID |
| POST | `/posts` | Create post |
| PUT | `/posts/{id}` | Update post |
| DELETE | `/posts/{id}` | Delete post |

## Run Tests

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

## CI/CD

The GitHub Actions pipeline includes:

1. Backend tests with pytest.
2. Trivy filesystem scan.
3. Optional SonarCloud analysis.
4. Docker build for backend and frontend.
5. Trivy image scans.
6. Push images to GitHub Container Registry on `main`.
7. Kubernetes deploy placeholder, with AWS/EKS intentionally left for you.

See [docs/ci-cd-github-actions.md](docs/ci-cd-github-actions.md) for the full setup guide.

## Environment Variables

| Variable | Default |
| --- | --- |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/blogdb` |
