# Expense Tracker

A Django + PostgreSQL expense tracking application built to demonstrate DevOps and Cloud skills including Docker, Kubernetes, Azure (AKS), CI/CD, and monitoring.

---

## Table of Contents

1. [About This Project](#about-this-project)
2. [Tech Stack](#tech-stack)
3. [Part 1: Run Locally](#part-1-run-locally)
4. [Part 2: DevOps Tasks](#part-2-devops-tasks)
   - [Phase 1: Dockerization](#phase-1-dockerization)
   - [Phase 2: Azure Setup](#phase-2-azure-setup)
   - [Phase 3: Kubernetes Deployment](#phase-3-kubernetes-deployment)
   - [Phase 4: CI/CD Pipeline](#phase-4-cicd-pipeline)
   - [Phase 5: Monitoring](#phase-5-monitoring)
   - [Phase 6: Ansible Automation](#phase-6-ansible-automation)
   - [Phase 7: Terraform (Future)](#phase-7-terraform-future)
5. [Skills Demonstrated](#skills-demonstrated)

---

## About This Project

This is a fully functional expense tracking web application. Your task is to:

1. First, run it locally and understand how it works
2. Then, containerize it with Docker
3. Deploy it to Azure Kubernetes Service (AKS)
4. Set up CI/CD, monitoring, and automation

This project will serve as a portfolio piece demonstrating your transition from DBA to DevOps/SRE.

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 4.2 (Python) |
| Database | PostgreSQL |
| Frontend | Django Templates + Bootstrap 5 |
| Containerization | Docker |
| Orchestration | Kubernetes (AKS) |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana |
| Configuration | Ansible |
| IaC | Terraform (future) |

---

## Part 1: Run Locally

Before doing any DevOps work, first run the application locally to understand what it does.

### Prerequisites

- Python 3.10+ installed
- PostgreSQL installed (or use SQLite for quick testing)
- Git installed

### Step 1: Clone and Setup

```bash
# Navigate to the project folder
cd expense-tracker

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Database

**Option A: Use SQLite (Quick Testing)**

Edit `expense_tracker/settings.py` and temporarily change the database config:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Option B: Use PostgreSQL (Recommended)**

1. Create a PostgreSQL database:
```sql
CREATE DATABASE expense_tracker;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE expense_tracker TO postgres;
```

2. Set environment variables (or create a `.env` file):
```bash
# Windows
set DB_NAME=expense_tracker
set DB_USER=postgres
set DB_PASSWORD=postgres
set DB_HOST=localhost
set DB_PORT=5432

# Linux/Mac
export DB_NAME=expense_tracker
export DB_USER=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432
```

### Step 3: Run Migrations

```bash
python manage.py migrate
```

### Step 4: Seed Initial Data

```bash
python manage.py seed_categories
```

This creates default expense categories (Food, Transport, Bills, etc.)

### Step 5: Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

### Step 6: Run the Application

```bash
python manage.py runserver
```

### Step 7: Test the Application

Open your browser and go to:

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Dashboard |
| http://127.0.0.1:8000/expenses/ | List all expenses |
| http://127.0.0.1:8000/expenses/add/ | Add new expense |
| http://127.0.0.1:8000/categories/ | Manage categories |
| http://127.0.0.1:8000/admin/ | Django admin panel |

**Try these actions:**
- Add a few expenses with different categories
- Edit an expense
- Delete an expense
- Filter expenses by category and date
- Check the dashboard for statistics

Once you understand how the app works, move on to Part 2.

---

## Part 2: DevOps Tasks

Now that you've seen the application running, it's time to containerize and deploy it.

---

### Phase 1: Dockerization

**Goal:** Create Docker images for the application and run it with Docker Compose.

#### Step 1.1: Create Dockerfile

Create a file named `Dockerfile` in the project root:

```dockerfile
# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "expense_tracker.wsgi:application"]
```

**Things to learn:**
- Multi-stage builds (optional optimization)
- Non-root user for security
- .dockerignore file
- Layer caching

#### Step 1.2: Create docker-compose.yml

Create a file named `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key-change-this
      - DB_NAME=expense_tracker
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_HOST=db
      - DB_PORT=5432
      - ALLOWED_HOSTS=localhost,127.0.0.1
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=expense_tracker
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Step 1.3: Create .dockerignore

Create a file named `.dockerignore`:

```
venv/
.env
__pycache__/
*.pyc
.git/
.gitignore
*.md
db.sqlite3
staticfiles/
```

#### Step 1.4: Build and Run

```bash
# Build the images
docker-compose build

# Start the containers
docker-compose up -d

# Run migrations inside container
docker-compose exec web python manage.py migrate

# Seed categories
docker-compose exec web python manage.py seed_categories

# Check logs
docker-compose logs -f

# Stop containers
docker-compose down
```

#### Step 1.5: Test

Open http://localhost:8000 and verify the app works.

**Checklist:**
- [ ] Dockerfile created with best practices
- [ ] docker-compose.yml with web + db services
- [ ] Application runs in containers
- [ ] Data persists in volume

---

### Phase 2: Azure Setup

**Goal:** Set up Azure resources needed for deployment.

#### Prerequisites

1. Azure account (free tier works)
2. Azure CLI installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

#### Step 2.1: Login to Azure

```bash
az login
```

#### Step 2.2: Create Resource Group

```bash
az group create --name expense-tracker-rg --location eastus
```

#### Step 2.3: Create Azure Container Registry (ACR)

```bash
# Create ACR (name must be globally unique)
az acr create \
  --resource-group expense-tracker-rg \
  --name shivaneeacr \
  --sku Basic

# Enable admin access
az acr update --name shivaneeacr --admin-enabled true

# Get login credentials
az acr credential show --name shivaneeacr
```

#### Step 2.4: Push Docker Image to ACR

```bash
# Login to ACR
az acr login --name shivaneeacr

# Tag your image
docker tag expense-tracker-web shivaneeacr.azurecr.io/expense-tracker:v1

# Push to ACR
docker push shivaneeacr.azurecr.io/expense-tracker:v1

# Verify
az acr repository list --name shivaneeacr
```

#### Step 2.5: Create AKS Cluster

```bash
# Create AKS cluster (this takes a few minutes)
az aks create \
  --resource-group expense-tracker-rg \
  --name expense-tracker-aks \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-managed-identity \
  --attach-acr shivaneeacr \
  --generate-ssh-keys

# Get credentials to use kubectl
az aks get-credentials \
  --resource-group expense-tracker-rg \
  --name expense-tracker-aks

# Verify connection
kubectl get nodes
```

**Checklist:**
- [ ] Resource group created
- [ ] ACR created and image pushed
- [ ] AKS cluster created
- [ ] kubectl configured and connected

---

### Phase 3: Kubernetes Deployment

**Goal:** Deploy the application to AKS using Kubernetes manifests.

#### Step 3.1: Create Kubernetes Directory

```bash
mkdir -p k8s
```

#### Step 3.2: Create Namespace

Create `k8s/namespace.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: expense-tracker
```

#### Step 3.3: Create Secrets

Create `k8s/secrets.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: expense-tracker-secrets
  namespace: expense-tracker
type: Opaque
stringData:
  SECRET_KEY: "your-super-secret-key-change-this-in-production"
  DB_PASSWORD: "postgres"
```

**Note:** In production, use Azure Key Vault or sealed-secrets instead of plain secrets.

#### Step 3.4: Create ConfigMap

Create `k8s/configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: expense-tracker-config
  namespace: expense-tracker
data:
  DEBUG: "False"
  DB_NAME: "expense_tracker"
  DB_USER: "postgres"
  DB_HOST: "postgres-service"
  DB_PORT: "5432"
  ALLOWED_HOSTS: "*"
```

#### Step 3.5: Create PostgreSQL StatefulSet

Create `k8s/postgres.yaml`:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: expense-tracker
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: expense-tracker
spec:
  serviceName: postgres-service
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
          image: postgres:15
          ports:
            - containerPort: 5432
          env:
            - name: POSTGRES_DB
              valueFrom:
                configMapKeyRef:
                  name: expense-tracker-config
                  key: DB_NAME
            - name: POSTGRES_USER
              valueFrom:
                configMapKeyRef:
                  name: expense-tracker-config
                  key: DB_USER
            - name: POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: expense-tracker-secrets
                  key: DB_PASSWORD
          volumeMounts:
            - name: postgres-storage
              mountPath: /var/lib/postgresql/data
      volumes:
        - name: postgres-storage
          persistentVolumeClaim:
            claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: expense-tracker
spec:
  selector:
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
  clusterIP: None
```

#### Step 3.6: Create Django Deployment

Create `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: expense-tracker
  namespace: expense-tracker
spec:
  replicas: 2
  selector:
    matchLabels:
      app: expense-tracker
  template:
    metadata:
      labels:
        app: expense-tracker
    spec:
      containers:
        - name: expense-tracker
          image: shivaneeacr.azurecr.io/expense-tracker:v1
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: expense-tracker-config
            - secretRef:
                name: expense-tracker-secrets
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /
              port: 8000
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: expense-tracker-service
  namespace: expense-tracker
spec:
  selector:
    app: expense-tracker
  ports:
    - port: 80
      targetPort: 8000
  type: LoadBalancer
```

#### Step 3.7: Create Horizontal Pod Autoscaler

Create `k8s/hpa.yaml`:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: expense-tracker-hpa
  namespace: expense-tracker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: expense-tracker
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

#### Step 3.8: Deploy to AKS

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/hpa.yaml

# Check status
kubectl get all -n expense-tracker

# Wait for external IP
kubectl get svc -n expense-tracker -w

# Run migrations (once pods are running)
kubectl exec -it deployment/expense-tracker -n expense-tracker -- python manage.py migrate

# Seed categories
kubectl exec -it deployment/expense-tracker -n expense-tracker -- python manage.py seed_categories
```

#### Step 3.9: Verify Deployment

```bash
# Get the external IP
kubectl get svc expense-tracker-service -n expense-tracker

# Open in browser: http://<EXTERNAL-IP>
```

**Checklist:**
- [ ] Namespace created
- [ ] Secrets and ConfigMaps configured
- [ ] PostgreSQL running with persistent storage
- [ ] Django app deployed with multiple replicas
- [ ] LoadBalancer service exposing the app
- [ ] HPA configured for auto-scaling
- [ ] Liveness and readiness probes working

---

### Phase 4: CI/CD Pipeline

**Goal:** Automate build and deployment using GitHub Actions.

#### Step 4.1: Create GitHub Repository

1. Create a new repository on GitHub
2. Push your code to the repository

```bash
git init
git add .
git commit -m "Initial commit - Expense Tracker app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/expense-tracker.git
git push -u origin main
```

#### Step 4.2: Add Azure Credentials to GitHub Secrets

1. Create a service principal:
```bash
az ad sp create-for-rbac \
  --name expense-tracker-github \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/expense-tracker-rg \
  --sdk-auth
```

2. In GitHub, go to Settings > Secrets and variables > Actions
3. Add these secrets:
   - `AZURE_CREDENTIALS`: The JSON output from the command above
   - `ACR_LOGIN_SERVER`: shivaneeacr.azurecr.io
   - `ACR_USERNAME`: (from az acr credential show)
   - `ACR_PASSWORD`: (from az acr credential show)

#### Step 4.3: Create GitHub Actions Workflow

Create `.github/workflows/deploy.yaml`:

```yaml
name: Build and Deploy to AKS

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  ACR_NAME: shivaneeacr
  AKS_CLUSTER: expense-tracker-aks
  RESOURCE_GROUP: expense-tracker-rg

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Login to ACR
        run: az acr login --name ${{ env.ACR_NAME }}

      - name: Build and push image
        run: |
          docker build -t ${{ env.ACR_NAME }}.azurecr.io/expense-tracker:${{ github.sha }} .
          docker push ${{ env.ACR_NAME }}.azurecr.io/expense-tracker:${{ github.sha }}
          docker tag ${{ env.ACR_NAME }}.azurecr.io/expense-tracker:${{ github.sha }} ${{ env.ACR_NAME }}.azurecr.io/expense-tracker:latest
          docker push ${{ env.ACR_NAME }}.azurecr.io/expense-tracker:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Get AKS credentials
        run: |
          az aks get-credentials \
            --resource-group ${{ env.RESOURCE_GROUP }} \
            --name ${{ env.AKS_CLUSTER }}

      - name: Update deployment image
        run: |
          kubectl set image deployment/expense-tracker \
            expense-tracker=${{ env.ACR_NAME }}.azurecr.io/expense-tracker:${{ github.sha }} \
            -n expense-tracker

      - name: Verify deployment
        run: kubectl rollout status deployment/expense-tracker -n expense-tracker
```

#### Step 4.4: Test the Pipeline

1. Make a small change to the code
2. Commit and push to main
3. Go to GitHub Actions tab and watch the workflow run
4. Verify the new version is deployed

**Checklist:**
- [ ] GitHub repository created
- [ ] Azure credentials configured in GitHub Secrets
- [ ] GitHub Actions workflow created
- [ ] Automatic build on push
- [ ] Automatic deployment to AKS

---

### Phase 5: Monitoring

**Goal:** Set up Prometheus and Grafana for cluster and application monitoring.

#### Step 5.1: Install Prometheus using Helm

```bash
# Add Helm repos
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Create monitoring namespace
kubectl create namespace monitoring

# Install Prometheus stack (includes Grafana)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin123
```

#### Step 5.2: Access Grafana

```bash
# Port forward to access Grafana
kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80

# Open http://localhost:3000
# Login: admin / admin123
```

#### Step 5.3: Explore Default Dashboards

Grafana comes with pre-built dashboards:
- Kubernetes / Compute Resources / Cluster
- Kubernetes / Compute Resources / Namespace (Pods)
- Node Exporter / Nodes

#### Step 5.4: Create Custom Dashboard

Create a dashboard for your expense-tracker app:
1. Go to Dashboards > New Dashboard
2. Add panels for:
   - Pod CPU usage
   - Pod Memory usage
   - Request rate
   - Response time

#### Step 5.5: (Optional) Add Application Metrics

Add django-prometheus to your app for application-specific metrics:

```bash
# Add to requirements.txt
django-prometheus
```

**Checklist:**
- [ ] Prometheus installed
- [ ] Grafana accessible
- [ ] Default dashboards working
- [ ] Custom dashboard created

---

### Phase 6: Ansible Automation

**Goal:** Use Ansible for configuration management and automation.

#### Step 6.1: Create Ansible Structure

```bash
mkdir -p ansible/{playbooks,roles,inventory}
```

#### Step 6.2: Create Inventory

Create `ansible/inventory/azure.yaml`:

```yaml
all:
  hosts:
    localhost:
      ansible_connection: local
```

#### Step 6.3: Create Playbook for Monitoring Setup

Create `ansible/playbooks/setup-monitoring.yaml`:

```yaml
---
- name: Setup Monitoring Stack on AKS
  hosts: localhost
  gather_facts: false

  vars:
    namespace: monitoring
    grafana_password: admin123

  tasks:
    - name: Add Prometheus Helm repo
      kubernetes.core.helm_repository:
        name: prometheus-community
        repo_url: https://prometheus-community.github.io/helm-charts

    - name: Create monitoring namespace
      kubernetes.core.k8s:
        name: "{{ namespace }}"
        api_version: v1
        kind: Namespace
        state: present

    - name: Install Prometheus stack
      kubernetes.core.helm:
        name: prometheus
        chart_ref: prometheus-community/kube-prometheus-stack
        namespace: "{{ namespace }}"
        values:
          grafana:
            adminPassword: "{{ grafana_password }}"

    - name: Display access instructions
      debug:
        msg: |
          Monitoring stack installed!
          Access Grafana: kubectl port-forward svc/prometheus-grafana -n monitoring 3000:80
          Login: admin / {{ grafana_password }}
```

#### Step 6.4: Create Playbook for App Deployment

Create `ansible/playbooks/deploy-app.yaml`:

```yaml
---
- name: Deploy Expense Tracker to AKS
  hosts: localhost
  gather_facts: false

  vars:
    namespace: expense-tracker
    image_tag: latest

  tasks:
    - name: Create namespace
      kubernetes.core.k8s:
        name: "{{ namespace }}"
        api_version: v1
        kind: Namespace
        state: present

    - name: Apply Kubernetes manifests
      kubernetes.core.k8s:
        state: present
        src: "{{ item }}"
      loop:
        - ../../k8s/secrets.yaml
        - ../../k8s/configmap.yaml
        - ../../k8s/postgres.yaml
        - ../../k8s/deployment.yaml
        - ../../k8s/hpa.yaml

    - name: Wait for deployment to be ready
      kubernetes.core.k8s_info:
        kind: Deployment
        namespace: "{{ namespace }}"
        name: expense-tracker
      register: deployment
      until: deployment.resources[0].status.readyReplicas == deployment.resources[0].spec.replicas
      retries: 30
      delay: 10
```

#### Step 6.5: Run Ansible Playbooks

```bash
# Install required collections
ansible-galaxy collection install kubernetes.core

# Run monitoring setup
ansible-playbook ansible/playbooks/setup-monitoring.yaml

# Run app deployment
ansible-playbook ansible/playbooks/deploy-app.yaml
```

**Checklist:**
- [ ] Ansible structure created
- [ ] Playbook for monitoring setup
- [ ] Playbook for app deployment
- [ ] Successfully run playbooks

---

### Phase 7: Terraform (Future)

**Goal:** Define all Azure infrastructure as code using Terraform.

This phase is for future learning. You'll create Terraform scripts to provision:
- Resource Group
- Azure Container Registry
- AKS Cluster
- Networking (VNet, Subnets)
- Azure Database for PostgreSQL (optional - managed DB)

#### Example Structure

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── providers.tf
└── modules/
    ├── aks/
    ├── acr/
    └── networking/
```

---

## Skills Demonstrated

After completing this project, you will have demonstrated:

| Skill | How It's Demonstrated |
|-------|----------------------|
| **Docker** | Containerized Django app with multi-stage builds |
| **Kubernetes** | Deployments, Services, StatefulSets, ConfigMaps, Secrets, PVC, HPA |
| **Azure** | AKS, ACR, Resource Groups, Azure CLI |
| **CI/CD** | GitHub Actions pipeline for automated deployment |
| **Monitoring** | Prometheus + Grafana setup and dashboards |
| **Ansible** | Playbooks for cluster setup and app deployment |
| **Linux** | Command line operations, shell scripting |
| **Database** | PostgreSQL deployment on Kubernetes |

---

## Clean Up Azure Resources

When you're done practicing, delete resources to avoid charges:

```bash
# Delete everything
az group delete --name expense-tracker-rg --yes --no-wait
```

---

## Useful Commands Reference

```bash
# Docker
docker build -t expense-tracker .
docker-compose up -d
docker-compose logs -f

# Kubernetes
kubectl get all -n expense-tracker
kubectl logs -f deployment/expense-tracker -n expense-tracker
kubectl exec -it deployment/expense-tracker -n expense-tracker -- /bin/sh
kubectl describe pod <pod-name> -n expense-tracker

# Azure
az aks get-credentials --resource-group expense-tracker-rg --name expense-tracker-aks
az acr login --name shivaneeacr

# Helm
helm list -n monitoring
helm uninstall prometheus -n monitoring
```

---

**Good luck, Shivanee! You've got this!**
