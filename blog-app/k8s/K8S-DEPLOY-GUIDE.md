# 🚀 Step 3: Thực Hành K8s Local với Kind

> Mục tiêu: Deploy toàn bộ ứng dụng MiniBlog (backend + frontend + postgres) lên Kubernetes cluster local bằng Kind.

---

## 📦 Phần 1: Cài Đặt Công Cụ

### 1.1 Cài Kind

**Kind** = Kubernetes in Docker — tạo K8s cluster bằng container Docker.

```bash
# Tải Kind binary về Windows
curl -Lo kind.exe https://kind.sigs.k8s.io/dl/v0.24.0/kind-windows-amd64

# Di chuyển vào thư mục trong PATH (có thể đổi chỗ khác)
mv kind.exe /usr/bin/kind.exe

# Kiểm tra
kind version
# Output: kind v0.24.0 go1.22.6 windows/amd64
```

> **Giải thích:** Kind chạy mỗi node K8s (control-plane, worker) như một container Docker. Bạn không cần VM hay cloud.

### 1.2 Kiểm tra kubectl

```bash
kubectl version --client
# Output: Client Version: v1.xx.x
```

> kubectl thường được cài kèm Docker Desktop. Nếu chưa có: `winget install Kubernetes.kubectl`

---

## ⚙️ Phần 2: Tạo Kind Cluster

### 2.1 File cấu hình cluster

Tạo file `blog-app/k8s/kind-config.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: miniblog
nodes:
  - role: control-plane
    extraPortMappings:
      - containerPort: 30080    # Port trên container Kind
        hostPort: 8081           # Port trên máy bạn
        protocol: TCP
      - containerPort: 30002
        hostPort: 8082
        protocol: TCP
  - role: worker
```

**Giải thích cấu hình:**
| Field | Ý nghĩa |
|-------|---------|
| `name: miniblog` | Tên cluster — dùng cho `kubectl context` |
| `role: control-plane` | Node chính (chạy etcd, api-server, scheduler) |
| `role: worker` | Node phụ (chạy pod ứng dụng) |
| `extraPortMappings` | Map port từ container Kind → localhost |
| `containerPort: 30080` | Port bên trong Kind (NodePort service sẽ dùng) |
| `hostPort: 8081` | Cổng bạn gõ trên browser `http://localhost:8081` |

### 2.2 Tạo cluster

```bash
# Tạo cluster từ file config
kind create cluster --config blog-app/k8s/kind-config.yaml
```

**Output mong đợi:**
```
Creating cluster "miniblog" ...
 ✓ Ensuring node image (kindest/node:v1.31.0)
 ✓ Preparing nodes 📦 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
 ✓ Joining worker nodes 🚜
Set kubectl context to "kind-miniblog"
```

### 2.3 Kiểm tra cluster

```bash
# Xem các node
kubectl get nodes
# Output:
# NAME                      STATUS   ROLES           AGE   VERSION
# miniblog-control-plane    Ready    control-plane   1m    v1.31.0
# miniblog-worker           Ready    <none>          1m    v1.31.0

# Xem context hiện tại
kubectl config current-context
# Output: kind-miniblog

# Xem tất cả pod trong cluster (namespace kube-system)
kubectl get pods -n kube-system
```

> **Khi nào cần xóa cluster?**
> ```bash
> kind delete cluster --name miniblog
> ```

---

## 🐳 Phần 3: Build & Load Docker Images vào Kind

### 3.1 Tại sao cần load image vào Kind?

Kind chạy trong Docker, không phải máy thật. Docker images trên máy bạn **không tự động có sẵn** trong Kind. Bạn phải:
1. **Build image** local
2. **Load image** vào Kind cluster (import vào container Docker của Kind)

### 3.2 Build images

```bash
cd blog-app

# Build backend image
docker build -t miniblog-backend:local ./backend

# Build frontend image  
docker build -t miniblog-frontend:local ./frontend
```

**Giải thích flag:**
| Flag | Ý nghĩa |
|------|---------|
| `-t miniblog-backend:local` | Tag image (tên:version) |
| `./backend` | Context directory (chứa Dockerfile) |

### 3.3 Load images vào Kind

```bash
# Load backend image vào Kind cluster
kind load docker-image miniblog-backend:local --name miniblog

# Load frontend image
kind load docker-image miniblog-frontend:local --name miniblog

# Kiểm tra image đã trong Kind chưa
docker exec miniblog-control-plane crictl images | grep miniblog
```

**Giải thích:** `kind load docker-image` copy image từ local Docker daemon vào container Kind. Nếu không load, K8s sẽ kéo từ registry (Docker Hub/GHCR) và không tìm thấy image local.

---

## 📄 Phần 4: Tạo K8s Manifests cho Local

### 4.1 Kiến thức cần nhớ

```
YAML K8s gồm 3 phần chính:
├── apiVersion: apps/v1      ← Phiên bản API
├── kind: Deployment          ← Loại resource
└── metadata:                 ← Thông tin cơ bản
    └── name, namespace
        └── spec:             ← Cấu hình chi tiết
```

### 4.2 Tạo namespace

File `blog-app/k8s/namespace.yaml`:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: blog-app
```

```bash
# Apply namespace
kubectl apply -f blog-app/k8s/namespace.yaml

# Kiểm tra
kubectl get namespaces | grep blog-app
```

### 4.3 Tạo Secret cho PostgreSQL

File `blog-app/k8s/postgres.yaml` (phần Secret):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
  namespace: blog-app
type: Opaque
stringData:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  POSTGRES_DB: blogdb
```

> **Secret vs ConfigMap:** Secret lưu dữ liệu nhạy cảm (base64), ConfigMap lưu config thường.

### 4.4 Tạo PVC cho PostgreSQL

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
  namespace: blog-app
spec:
  accessModes:
    - ReadWriteOnce       # Chỉ 1 pod ghi được
  resources:
    requests:
      storage: 5Gi        # Xin 5GB dung lượng
```

> **Lưu ý:** Kind tự động tạo StorageClass mặc định dùng hostPath. Dữ liệu mất khi xóa cluster!

### 4.5 Tạo Deployment + Service cho PostgreSQL

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: blog-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine     # Kéo từ Docker Hub
          imagePullPolicy: IfNotPresent # Chỉ kéo nếu chưa có
          ports:
            - containerPort: 5432
          envFrom:
            - secretRef:
                name: postgres-secret   # Lấy env từ Secret
          volumeMounts:
            - name: postgres-data
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-data
          persistentVolumeClaim:
            claimName: postgres-data
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: blog-app
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```

**Giải thích:**
| Field | Ý nghĩa |
|-------|---------|
| `spec.selector.matchLabels` | Deployment quản lý pod có label nào |
| `template.metadata.labels` | Gán label cho pod (phải match selector) |
| `envFrom.secretRef` | Inject toàn bộ key trong Secret thành env var |
| `volumeMounts` | Gắn volume vào đường dẫn trong container |
| `Service.selector` | Service chuyển traffic đến pod có label này |
| `port: 5432` → `targetPort: 5432` | Port service → port container |

### 4.6 Backend Deployment + Service (dùng image local)

**Thay đổi so với file gốc:**
- `image: miniblog-backend:local` (thay vì ghcr.io/...)
- `imagePullPolicy: IfNotPresent` (thay vì Always)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: blog-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: miniblog-backend:local    # Image local đã load vào Kind
          imagePullPolicy: IfNotPresent    # Không kéo từ registry
          ports:
            - containerPort: 8000
          env:
            - name: DATABASE_URL
              value: postgresql://postgres:postgres@postgres:5432/blogdb
          # ... readinessProbe, livenessProbe, resources...
---
apiVersion: v1
kind: Service
metadata:
  name: backend
  namespace: blog-app
spec:
  selector:
    app: backend
  ports:
    - port: 8000
      targetPort: 8000
```

> **Quan trọng:** `DATABASE_URL` dùng `postgres:5432` — đây là tên Service của PostgreSQL. K8s DNS tự động resolve tên service thành IP cluster.

### 4.7 Frontend Deployment + Service (NodePort)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: blog-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: frontend
          image: miniblog-frontend:local
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: blog-app
spec:
  type: NodePort                # ← Quan trọng: expose ra ngoài cluster
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 80
      nodePort: 30080           # Port trên Node (phải 30000-32767)
```

**So sánh Service types:**
| Type | Truy cập từ | Dùng khi |
|------|------------|----------|
| `ClusterIP` (mặc định) | Trong cluster | Backend gọi DB |
| `NodePort` | `localhost:<nodePort>` | Local test |
| `LoadBalancer` | IP ngoài | Cloud (AWS/GCP) |

### 4.8 Mối quan hệ giữa Kind port và Service NodePort

```
Browser bạn          Kind Node            Pod Container
:8081 ────▶ hostPort ────▶ :30080 ────▶ :80 (Nginx)
                       (nodePort)     (targetPort)
```

Cấu hình trong `kind-config.yaml`:
```yaml
extraPortMappings:
  - containerPort: 30080    # ← NodePort trong Service
    hostPort: 8081           # ← Cổng bạn gõ browser
```

---

## 🚀 Phần 5: Deploy lên Kind

### 5.1 Apply tất cả manifests

```bash
cd blog-app

# 1. Namespace (phải apply trước)
kubectl apply -f k8s/namespace.yaml

# 2. Secret + PVC + Postgres
kubectl apply -f k8s/postgres.yaml

# 3. Backend
kubectl apply -f k8s/backend.yaml

# 4. Frontend
kubectl apply -f k8s/frontend.yaml
```

### 5.2 Kiểm tra deployment

```bash
# Xem tất cả resource trong namespace blog-app
kubectl get all -n blog-app

# Output mong đợi:
# NAME                           READY   STATUS    RESTARTS   AGE
# pod/backend-xxxx              1/1     Running   0          1m
# pod/frontend-xxxx             1/1     Running   0          1m
# pod/postgres-xxxx             1/1     Running   0          1m
#
# NAME               TYPE        CLUSTER-IP     PORT(S)        AGE
# service/backend    ClusterIP   10.96.x.x      8000/TCP       1m
# service/frontend   NodePort    10.96.x.x      80:30080/TCP   1m
# service/postgres   ClusterIP   10.96.x.x      5432/TCP       1m
#
# NAME                      READY   UP-TO-DATE   AVAILABLE
# deployment.apps/backend   2/2     2            2
# deployment.apps/frontend  2/2     2            2
# deployment.apps/postgres  1/1     1            1
```

### 5.3 Debug nếu pod không chạy

```bash
# Xem chi tiết pod bị lỗi
kubectl describe pod -n blog-app <pod-name>

# Xem log
kubectl logs -n blog-app <pod-name>

# Xem event (lý do tại sao pod fail)
kubectl get events -n blog-app --sort-by='.lastTimestamp'
```

**Các trạng thái pod thường gặp:**
| Status | Ý nghĩa | Cách fix |
|--------|---------|----------|
| `Pending` | Chưa schedule được | Thiếu tài nguyên, kiểm tra `kubectl describe` |
| `ContainerCreating` | Đang kéo image | Chờ, hoặc imagePullPolicy sai |
| `CrashLoopBackOff` | Start xong crash liên tục | Xem log: `kubectl logs` |
| `ImagePullBackOff` | Kéo image thất bại | Image không tồn tại hoặc sai tag |

### 5.4 Kiểm tra ứng dụng hoạt động

```bash
# Frontend (qua NodePort 30080 → host 8081)
curl http://localhost:8081

# Backend health check
curl http://localhost:8082/health

# Backend API - tạo bài viết
curl -X POST http://localhost:8082/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello K8s","content":"MiniBlog running on Kind!"}'

# Lấy danh sách bài viết
curl http://localhost:8082/posts
```

---

## 🎯 Phần 6: Commands Tổng Kết

### Cheat Sheet cho Kind

```bash
# Tạo cluster
kind create cluster --config kind-config.yaml

# Xóa cluster
kind delete cluster --name miniblog

# Load image
kind load docker-image miniblog-backend:local --name miniblog

# Xem các cluster
kind get clusters
```

### Cheat Sheet cho kubectl

```bash
# Cơ bản
kubectl get all -n blog-app
kubectl get pods -n blog-app -o wide     # Xem thêm IP, Node
kubectl get svc -n blog-app              # Chỉ xem Service
kubectl get deployments -n blog-app       # Chỉ xem Deployment

# Chi tiết
kubectl describe pod -n blog-app backend-xxx
kubectl logs -n blog-app -l app=backend  # Log tất cả pod có label app=backend

# Debug
kubectl exec -n blog-app -it backend-xxx -- /bin/bash  # Vào container
kubectl port-forward -n blog-app svc/backend 8003:8000  # Forward port tạm

# Xóa
kubectl delete -f k8s/backend.yaml
kubectl delete all --all -n blog-app     # Xóa tất cả trong namespace
```

### Lưu ý quan trọng
> ⚠️ **Kind là môi trường tạm:** Khi xóa cluster, toàn bộ dữ liệu PostgreSQL mất!
> Để xóa hoàn toàn: `kind delete cluster --name miniblog`
> Để clean images: `docker system prune -a`
