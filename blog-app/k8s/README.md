# Kubernetes Manifests

These manifests are cloud-neutral on purpose. Replace the image placeholders before applying:

```bash
sed -i "s|ghcr.io/OWNER/REPOSITORY-backend:latest|ghcr.io/<owner>/<repo>-backend:latest|g" k8s/backend.yaml
sed -i "s|ghcr.io/OWNER/REPOSITORY-frontend:latest|ghcr.io/<owner>/<repo>-frontend:latest|g" k8s/frontend.yaml
```

Apply after your Kubernetes cluster is ready:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress-placeholder.yaml
```

The AWS/EKS, storage class, ALB controller, domain, and certificate setup are intentionally left for you.
