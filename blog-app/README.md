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
SE359-DevOps/
|-- .github/
|   `-- workflows/
|       `-- ci-cd.yml
`-- blog-app/
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

## GitHub Actions Pipeline Code

The workflow is stored at:

```text
.github/workflows/ci-cd.yml
```

### Trigger

The pipeline runs on push, pull request, or manual dispatch:

```yaml
name: DevSecOps CI/CD

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]
  workflow_dispatch:
    inputs:
      deploy_to_kubernetes:
        description: "Run the Kubernetes deploy placeholder after images are published"
        required: false
        default: "false"
        type: choice
        options: ["false", "true"]
```

### Test Stage

This stage installs backend dependencies and runs FastAPI tests with SQLite:

```yaml
test:
  name: Test backend
  runs-on: ubuntu-latest

  steps:
    - name: Checkout source
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.11"
        cache: pip
        cache-dependency-path: blog-app/backend/requirements.txt

    - name: Install dependencies
      working-directory: blog-app/backend
      run: pip install -r requirements.txt

    - name: Run unit tests
      working-directory: blog-app/backend
      env:
        DATABASE_URL: sqlite:///./test.db
      run: pytest -v --junitxml=pytest-report.xml
```

### Trivy Filesystem Scan

This stage scans the source code and dependency files:

```yaml
filesystem-scan:
  name: Trivy filesystem scan
  runs-on: ubuntu-latest
  needs: test

  steps:
    - name: Checkout source
      uses: actions/checkout@v4

    - name: Scan repository
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: fs
        scan-ref: blog-app
        format: table
        output: trivy-fs-report.txt
        severity: HIGH,CRITICAL
        ignore-unfixed: true
        exit-code: "0"
```

### Optional SonarCloud Analysis

This job runs only when SonarCloud variables are configured:

```yaml
sonarcloud:
  name: SonarCloud analysis
  runs-on: ubuntu-latest
  needs: test
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_PROJECT_KEY: ${{ vars.SONAR_PROJECT_KEY }}
    SONAR_ORGANIZATION: ${{ vars.SONAR_ORGANIZATION }}

  steps:
    - name: Run SonarCloud scan
      if: env.SONAR_TOKEN != '' && env.SONAR_PROJECT_KEY != '' && env.SONAR_ORGANIZATION != ''
      uses: SonarSource/sonarqube-scan-action@v5
      with:
        args: >
          -Dsonar.projectKey=${{ env.SONAR_PROJECT_KEY }}
          -Dsonar.organization=${{ env.SONAR_ORGANIZATION }}
          -Dsonar.sources=blog-app/backend,blog-app/frontend
          -Dsonar.tests=blog-app/backend
          -Dsonar.python.version=3.11
```

### Docker Build, Scan, and Push

The pipeline builds backend and frontend images, scans them with Trivy, and pushes them to GHCR:

```yaml
build-and-publish:
  name: Build, scan, and publish images
  runs-on: ubuntu-latest
  needs: [test, filesystem-scan]

  steps:
    - name: Build backend image
      run: docker build -t "$BACKEND_IMAGE:ci" ./blog-app/backend

    - name: Scan backend image
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.BACKEND_IMAGE }}:ci
        severity: HIGH,CRITICAL
        ignore-unfixed: true
        exit-code: "0"

    - name: Build frontend image
      run: docker build -t "$FRONTEND_IMAGE:ci" ./blog-app/frontend

    - name: Scan frontend image
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: ${{ env.FRONTEND_IMAGE }}:ci
        severity: HIGH,CRITICAL
        ignore-unfixed: true
        exit-code: "0"

    - name: Log in to GitHub Container Registry
      uses: docker/login-action@v3
      with:
        registry: ghcr.io
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
```

### AWS/EKS Placeholder

The AWS deployment job is intentionally left as a placeholder:

```yaml
deploy-placeholder:
  name: AWS/EKS deploy placeholder
  runs-on: ubuntu-latest
  needs: build-and-publish
  if: github.event_name == 'workflow_dispatch' && inputs.deploy_to_kubernetes == 'true'

  steps:
    - name: Show next AWS steps
      run: |
        echo "AWS/EKS is intentionally left for you."
        echo "After you create the cluster and configure kubeconfig, deploy with:"
        echo "kubectl apply -f blog-app/k8s/"
```

## Docker Commands

Build and run the full stack locally:

```bash
cd blog-app
docker compose up --build
```

Build images manually:

```bash
docker build -t blog-backend ./blog-app/backend
docker build -t blog-frontend ./blog-app/frontend
```

Published image format:

```text
ghcr.io/<owner>/<repo>-backend:latest
ghcr.io/<owner>/<repo>-frontend:latest
ghcr.io/<owner>/<repo>-backend:<commit-sha>
ghcr.io/<owner>/<repo>-frontend:<commit-sha>
```

## Kubernetes Commands

After you create your Kubernetes cluster, update the image names in `k8s/backend.yaml` and `k8s/frontend.yaml`, then apply:

```bash
kubectl apply -f blog-app/k8s/namespace.yaml
kubectl apply -f blog-app/k8s/postgres.yaml
kubectl apply -f blog-app/k8s/backend.yaml
kubectl apply -f blog-app/k8s/frontend.yaml
kubectl apply -f blog-app/k8s/ingress-placeholder.yaml
```

Check deployment status:

```bash
kubectl get pods -n blog-app
kubectl get svc -n blog-app
kubectl get ingress -n blog-app
```

## AWS Section

This part is intentionally left for manual setup:

```text
1. Create AWS IAM user/role.
2. Create EKS cluster.
3. Configure kubectl context.
4. Install AWS Load Balancer Controller or another ingress controller.
5. Configure domain and TLS.
6. Apply Kubernetes manifests.
7. Add monitoring with Prometheus and Grafana if needed.
```

## Environment Variables

| Variable | Default |
| --- | --- |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/blogdb` |
