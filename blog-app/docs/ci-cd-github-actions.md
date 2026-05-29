# CI/CD With GitHub Actions

This setup follows the same learning flow as a production DevOps blog-app project, but replaces Jenkins, Nexus, and DockerHub with GitHub Actions and GitHub Container Registry.

## Tool Mapping

| Original style | This project |
| --- | --- |
| Jenkins pipeline | GitHub Actions workflow |
| Nexus artifact repository | GitHub Actions artifacts |
| DockerHub registry | GitHub Container Registry |
| Trivy scan stages | Trivy filesystem and image scans |
| SonarQube/SonarCloud | Optional SonarCloud job |
| Kubernetes/EKS deploy | Kubernetes manifests, AWS left for you |
| Prometheus/Grafana | Optional after deployment |

## Pipeline Stages

1. Checkout source code.
2. Install Python dependencies.
3. Run FastAPI tests with pytest.
4. Upload pytest report as a workflow artifact.
5. Run Trivy filesystem scan.
6. Run optional SonarCloud analysis when `SONAR_TOKEN` is configured.
7. Build backend and frontend Docker images.
8. Run Trivy image scans.
9. Push images to GitHub Container Registry on `main`.
10. Leave Kubernetes/AWS deployment as a manual placeholder.

## GitHub Secrets

Required:

```text
No custom secret is required for GHCR.
GitHub Actions uses GITHUB_TOKEN automatically.
```

Optional:

```text
SONAR_TOKEN
```

Optional GitHub repository variables:

```text
SONAR_PROJECT_KEY
SONAR_ORGANIZATION
```

Use these only if you connect the repository to SonarCloud.

## Image Names

After a successful push to `main`, the workflow publishes:

```text
ghcr.io/<owner>/<repo>-backend:latest
ghcr.io/<owner>/<repo>-frontend:latest
ghcr.io/<owner>/<repo>-backend:<commit-sha>
ghcr.io/<owner>/<repo>-frontend:<commit-sha>
```

## AWS Part Left For You

You can do these steps yourself:

1. Create AWS account/IAM permissions.
2. Create EKS cluster or another Kubernetes cluster.
3. Configure `kubectl` access.
4. Install an ingress controller or AWS Load Balancer Controller.
5. Replace image placeholders in `k8s/backend.yaml` and `k8s/frontend.yaml`.
6. Apply Kubernetes manifests.
7. Add domain, TLS, monitoring, and alerting.

## Commands

Run locally:

```bash
docker compose up --build
```

Run tests locally:

```bash
cd backend
pip install -r requirements.txt
pytest -v
```

Deploy manifests after your cluster is ready:

```bash
kubectl apply -f k8s/
```
