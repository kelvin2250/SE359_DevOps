# Kubernetes Manifests

These manifests are cloud-neutral on purpose. Replace the image placeholders before applying:

```bash
sed -i "s|ghcr.io/OWNER/REPOSITORY-backend:latest|ghcr.io/<owner>/<repo>-backend:latest|g" k8s/backend.yaml
sed -i "s|ghcr.io/OWNER/REPOSITORY-frontend:latest|ghcr.io/<owner>/<repo>-frontend:latest|g" k8s/frontend.yaml
```

## Apply (sau khi cluster sẵn sàng)

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
```

## Ingress (chọn 1 trong 2)

### Option 1: Nginx Ingress Controller (local hoặc cloud)
```bash
# Cài Nginx Ingress Controller trước
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.1/deploy/static/provider/cloud/deploy.yaml

# Apply ingress
kubectl apply -f k8s/ingress.yaml
```

### Option 2: AWS Load Balancer (EKS - production)
```bash
# Cài AWS Load Balancer Controller trước
# Sau đó apply ingress cho ALB
kubectl apply -f k8s/ingress-aws.yaml
```

## Lưu ý
- Thay `blog.example.com` trong file ingress bằng domain thật của bạn
- Cấu hình TLS/certificate (cert-manager cho Nginx, ACM cho AWS)
- Storage class, domain, và certificate setup tùy thuộc vào cloud provider
