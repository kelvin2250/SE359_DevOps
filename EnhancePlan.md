# 📋 Kế Hoạch Nâng Cấp Đồ Án Cuối Kỳ - MiniBlog DevOps

> **Môn học:** SE359 - DevOps  
> **Project:** InkNotes (MiniBlog) - FastAPI + PostgreSQL + Nginx  
> **Mục tiêu:** Hoàn thiện pipeline DevOps từ code → production

---

## ✅ Đã Hoàn Thành

| STT | Hạng mục | Chi tiết | Trạng thái |
|-----|----------|----------|------------|
| 1 | **Docker Compose** | 3 service: backend, frontend, postgres | ✅ |
| 2 | **Dockerfile** | Multi-stage backend (Python slim) + frontend (Nginx) | ✅ |
| 3 | **CI/CD Pipeline** | GitHub Actions: test, hadolint, checkov, trivy, build, push GHCR | ✅ |
| 4 | **Security Scanning** | Hadolint (Dockerfile), Checkov (K8s), Trivy (image/fs) | ✅ |
| 5 | **K8s Manifests** | backend, frontend, postgres, network-policy, ingress | ✅ |
| 6 | **Helm Chart** | Chart + templates + values (dev/prod) | ⚠️ Cần fix |
| 7 | **Kind Cluster** | Local K8s cluster + deploy guide | ⚠️ Cần fix |

---

## 📌 Các Bước Kế Tiếp (Theo Thứ Tự Ưu Tiên)

---

### 🔴 Bước 1: Fix Helm Deploy trên Kind 

**Vấn đề hiện tại:**
- Postgres không chạy được trên Windows/Kind do permission filesystem
- Frontend Nginx cần chạy root mới bind được port 80

**Cần làm:**
- [ ] Chạy thành công `helm install` với cả 3 pod (postgres, backend, frontend)
- [ ] Test API hoạt động: `curl http://localhost:8081` trả về HTML
- [ ] Test CRUD: tạo/sửa/xóa bài viết qua frontend UI
- [ ] Chụp screenshot kết quả để đưa vào báo cáo

**Output mong đợi:**
```bash
kubectl get pods -n blog-app
# All 3 pods: Running
curl http://localhost:8081
# <html>... trả về frontend
curl http://localhost:8082/posts
# [] - danh sách bài viết
```

---

### 🟡 Bước 2: Hoàn Thiện CI/CD Pipeline 

**Hiện tại:** CI chạy nhưng còn thiếu tự động hóa cho deployment.

**Cần làm:**
- [ ] Push code → CI tự động build image + push GHCR
- [ ] Cập nhật image tag trong Helm values tự động
- [ ] Thêm badge CI vào README.md:
  ```markdown
  ![CI](https://github.com/kelvin2250/SE359_DevOps/actions/workflows/ci-cd.yml/badge.svg)
  ```
- [ ] Chụp screenshot GitHub Actions chạy xanh (all green)

---

### 🟢 Bước 3: Monitoring - Prometheus + Grafana 

**Mục tiêu:** Thấy được metrics thực tế của ứng dụng.

**Cần làm:**

#### 3.1 Thêm metrics vào backend
- [ ] Cài `prometheus_client` vào `requirements.txt`
- [ ] Thêm endpoint `/metrics` trong `main.py`:
  - `http_requests_total` (Counter) - đếm request
  - `http_request_duration_seconds` (Histogram) - thời gian xử lý
  - `posts_created_total` (Counter) - số bài viết tạo
- [ ] Test local: `curl http://localhost:8002/metrics`

#### 3.2 Cài Prometheus + Grafana
- [ ] Tạo file `blog-app/monitoring/docker-compose.monitoring.yml`
- [ ] Prometheus scrape config trỏ đến backend `/metrics`
- [ ] Grafana dashboard: số request, response time, error rate
- [ ] Chụp screenshot dashboard Grafana

**File cần tạo:**
```
blog-app/monitoring/
├── docker-compose.monitoring.yml
├── prometheus/
│   └── prometheus.yml
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── datasource.yml
        └── dashboards/
            └── blog-dashboard.json
```

---

### 🔵 Bước 4: GitOps - ArgoCD 

**Mục tiêu:** Push code → tự động deploy lên K8s.

**Cần làm:**

#### 4.1 Cài ArgoCD vào Kind
- [ ] `kubectl create namespace argocd`
- [ ] `kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml`
- [ ] Port-forward ArgoCD UI: `kubectl port-forward svc/argocd-server -n argocd 8083:443`

#### 4.2 Tạo ArgoCD Application
- [ ] File `blog-app/gitops/application.yaml`:
  ```yaml
  apiVersion: argoproj.io/v1alpha1
  kind: Application
  metadata:
    name: miniblog
  spec:
    source:
      repoURL: https://github.com/kelvin2250/SE359_DevOps
      path: blog-app/helm/miniblog
      targetRevision: main
    destination:
      namespace: blog-app
    syncPolicy:
      automated:
        prune: true
        selfHeal: true
  ```
- [ ] Chụp screenshot ArgoCD UI: app status "Synced"

**File cần tạo:**
```
blog-app/gitops/
└── application.yaml
```

---

### 🟣 Bước 5: Tài Liệu & Báo Cáo 

**Mục tiêu:** Hoàn thiện tài liệu cho đồ án.

**Cần làm:**

- [ ] Cập nhật `README.md` với:
  - Mô tả kiến trúc tổng quan (có sơ đồ)
  - Hướng dẫn cài đặt step-by-step
  - Hướng dẫn chạy local (Docker Compose + Kind)
  - Hướng dẫn CI/CD
  - Badge CI
  - Danh sách công nghệ sử dụng

- [ ] Tạo file `DEVOPS-REPORT.md` cho báo cáo môn học:
  - Giới thiệu project
  - Kiến trúc hệ thống (có diagram Mermaid)
  - Các công nghệ DevOps đã áp dụng
  - Pipeline CI/CD (có screenshot)
  - K8s deployment (có screenshot)
  - Monitoring (có screenshot)
  - GitOps với ArgoCD (có screenshot)
  - Kết luận và bài học

---

### 🎯 Bước 6: Deploy AWS EKS

**Chỉ làm nếu có tài khoản AWS và thời gian.**

- [ ] Tạo EKS cluster (hoặc dùng eksctl)
- [ ] Cài AWS Load Balancer Controller
- [ ] Cấu hình domain + TLS (cert-manager + Let's Encrypt)
- [ ] Deploy Helm chart lên EKS
- [ ] Chụp screenshot ứng dụng chạy trên cloud

---

## 📊 Tổng Quan Timeline 

```mermaid
gantt
    title Lộ trình hoàn thiện đồ án
    dateFormat  YYYY-MM-DD
    section Tuần 1
    Fix Helm trên Kind           :a1, 7d
    Hoàn thiện CI/CD             :a2, 3d
    section Tuần 2
    Prometheus + Grafana         :b1, 7d
    section Tuần 3
    ArgoCD GitOps                :c1, 7d
    section Tuần 4
    Tài liệu + Báo cáo           :d1, 5d
    AWS EKS (optional)           :d2, 5d
```

## 📝 Checklist Tổng Kết

| Bước | Hạng mục | File ảnh hưởng | Khó |
|------|----------|---------------|-----|
| 1 | Fix Helm Kind | `helm/miniblog/*` | ⭐⭐ |
| 2 | CI/CD hoàn chỉnh | `.github/workflows/ci-cd.yml` | ⭐ |
| 3 | Prometheus + Grafana | `backend/main.py`, `monitoring/*` | ⭐⭐⭐ |
| 4 | ArgoCD | `gitops/application.yaml` | ⭐⭐⭐ |
| 5 | Tài liệu | `README.md`, `DEVOPS-REPORT.md` | ⭐ |
| 6 | AWS EKS | `k8s/*`, `helm/*` | ⭐⭐⭐⭐ |
