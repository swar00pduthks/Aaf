# Azure Deployment Guide

Complete guide for deploying Personal Finance Agent on Azure Kubernetes Service (AKS) with Azure OpenAI.

## Prerequisites

- Azure subscription
- Azure CLI installed
- kubectl installed
- Helm 3 installed
- Docker installed

## Step 1: Create Azure Resources

### 1.1 Create Resource Group

```bash
# Set variables
RESOURCE_GROUP="finance-agent-rg"
LOCATION="eastus"
AKS_NAME="finance-aks"
ACR_NAME="financeagentacr"  # Must be globally unique

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 1.2 Create Azure Container Registry (ACR)

```bash
# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Standard

# Enable admin user
az acr update \
  --name $ACR_NAME \
  --admin-enabled true

# Get credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

echo "ACR Login Server: $ACR_LOGIN_SERVER"
```

### 1.3 Create AKS Cluster

```bash
# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME \
  --node-count 3 \
  --node-vm-size Standard_D4s_v3 \
  --enable-addons monitoring \
  --enable-managed-identity \
  --attach-acr $ACR_NAME \
  --generate-ssh-keys

# Get credentials
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name $AKS_NAME

# Verify connection
kubectl get nodes
```

### 1.4 Create Azure OpenAI Service

```bash
OPENAI_NAME="finance-openai"

# Create Azure OpenAI resource
az cognitiveservices account create \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind OpenAI \
  --sku S0 \
  --location $LOCATION

# Get endpoint and key
AZURE_OPENAI_ENDPOINT=$(az cognitiveservices account show \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query properties.endpoint --output tsv)

AZURE_OPENAI_API_KEY=$(az cognitiveservices account keys list \
  --name $OPENAI_NAME \
  --resource-group $RESOURCE_GROUP \
  --query key1 --output tsv)

echo "Azure OpenAI Endpoint: $AZURE_OPENAI_ENDPOINT"
```

### 1.5 Create Azure OpenAI Deployments

Go to Azure OpenAI Studio (https://oai.azure.com) and create deployments:

1. **GPT-4 Deployment**
   - Name: `gpt-4-deployment`
   - Model: `gpt-4`
   - Version: Latest

2. **GPT-3.5 Turbo Deployment**
   - Name: `gpt-35-turbo-deployment`
   - Model: `gpt-35-turbo`
   - Version: Latest

### 1.6 Create Azure Database for PostgreSQL

```bash
DB_SERVER_NAME="finance-db-server"
DB_NAME="finance_db"
DB_USERNAME="financeadmin"
DB_PASSWORD="YourSecurePassword123!"  # Change this!

# Create PostgreSQL server
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $DB_SERVER_NAME \
  --location $LOCATION \
  --admin-user $DB_USERNAME \
  --admin-password $DB_PASSWORD \
  --sku-name Standard_D2s_v3 \
  --tier GeneralPurpose \
  --storage-size 128 \
  --version 14

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $DB_SERVER_NAME \
  --database-name $DB_NAME

# Get connection string
DB_HOST="${DB_SERVER_NAME}.postgres.database.azure.com"
DATABASE_URL="postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}?sslmode=require"
```

### 1.7 Create Azure Cache for Redis

```bash
REDIS_NAME="finance-cache"

# Create Redis cache
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name $REDIS_NAME \
  --location $LOCATION \
  --sku Standard \
  --vm-size c1

# Get connection details
REDIS_HOST=$(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query hostName --output tsv)
REDIS_PASSWORD=$(az redis list-keys --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query primaryKey --output tsv)
```

## Step 2: Build and Push Docker Images

### 2.1 Build Backend Image

```bash
cd examples/personal_finance_agent

# Build backend
docker build -t $ACR_LOGIN_SERVER/finance-backend:1.0.0 \
  -f Dockerfile.backend .

# Push to ACR
docker push $ACR_LOGIN_SERVER/finance-backend:1.0.0
```

### 2.2 Build Frontend Image

```bash
# Build frontend
docker build -t $ACR_LOGIN_SERVER/finance-frontend:1.0.0 \
  -f Dockerfile.frontend ./frontend

# Push to ACR
docker push $ACR_LOGIN_SERVER/finance-frontend:1.0.0
```

## Step 3: Create Kubernetes Secrets

### 3.1 Create ACR Pull Secret

```bash
kubectl create secret docker-registry acr-secret \
  --docker-server=$ACR_LOGIN_SERVER \
  --docker-username=$ACR_USERNAME \
  --docker-password=$ACR_PASSWORD
```

### 3.2 Create Azure OpenAI Secret

```bash
kubectl create secret generic azure-openai-secret \
  --from-literal=AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY
```

### 3.3 Create Database Secret

```bash
kubectl create secret generic postgres-secret \
  --from-literal=username=$DB_USERNAME \
  --from-literal=password=$DB_PASSWORD \
  --from-literal=url=$DATABASE_URL
```

### 3.4 Create Redis Secret

```bash
kubectl create secret generic redis-secret \
  --from-literal=password=$REDIS_PASSWORD
```

## Step 4: Deploy with Helm

### 4.1 Update values.yaml

Edit `helm/personal-finance-agent/values.yaml`:

```yaml
backend:
  image:
    repository: YOUR-ACR-NAME.azurecr.io/finance-backend
    tag: "1.0.0"

frontend:
  image:
    repository: YOUR-ACR-NAME.azurecr.io/finance-frontend
    tag: "1.0.0"

azureOpenAI:
  endpoint: "YOUR-AZURE-OPENAI-ENDPOINT"
  deployments:
    gpt4: "gpt-4-deployment"
    gpt35turbo: "gpt-35-turbo-deployment"

database:
  host: "YOUR-DB-HOST.postgres.database.azure.com"

redis:
  azure:
    host: "YOUR-REDIS-HOST.redis.cache.windows.net"

ingress:
  hosts:
    - host: finance.yourdomain.com
```

### 4.2 Install Helm Chart

```bash
cd helm

# Install
helm install finance-agent ./personal-finance-agent \
  --namespace finance \
  --create-namespace

# Or upgrade
helm upgrade --install finance-agent ./personal-finance-agent \
  --namespace finance \
  --create-namespace
```

### 4.3 Verify Deployment

```bash
# Check pods
kubectl get pods -n finance

# Check services
kubectl get svc -n finance

# Check ingress
kubectl get ingress -n finance

# View logs
kubectl logs -n finance -l app.kubernetes.io/component=backend --tail=100
```

## Step 5: Configure DNS

### 5.1 Get Ingress IP

```bash
INGRESS_IP=$(kubectl get ingress -n finance finance-agent-personal-finance-agent -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Ingress IP: $INGRESS_IP"
```

### 5.2 Create DNS Record

Create an A record in your DNS provider:
- Name: `finance`
- Type: `A`
- Value: `<INGRESS_IP>`
- TTL: `300`

## Step 6: Install Cert-Manager (SSL)

```bash
# Add Jetstack repo
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set installCRDs=true

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Step 7: Access Application

```bash
# Get URL
echo "Application URL: https://finance.yourdomain.com"

# Test backend
curl https://finance.yourdomain.com/api/health

# Test frontend
open https://finance.yourdomain.com
```

## Monitoring & Troubleshooting

### View Logs

```bash
# Backend logs
kubectl logs -n finance -l app.kubernetes.io/component=backend -f

# Frontend logs
kubectl logs -n finance -l app.kubernetes.io/component=frontend -f

# All logs
kubectl logs -n finance --all-containers=true -f
```

### Describe Resources

```bash
kubectl describe deployment -n finance
kubectl describe pod -n finance <pod-name>
kubectl describe ingress -n finance
```

### Check Events

```bash
kubectl get events -n finance --sort-by='.lastTimestamp'
```

## Scaling

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment -n finance finance-agent-personal-finance-agent-backend --replicas=5

# Scale frontend
kubectl scale deployment -n finance finance-agent-personal-finance-agent-frontend --replicas=3
```

### Auto-scaling (HPA)

Already configured in `values.yaml`:

```yaml
backend:
  autoscaling:
    enabled: true
    minReplicas: 3
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70
```

## Backup & Restore

### Database Backup

```bash
# Manual backup
kubectl exec -n finance $(kubectl get pod -n finance -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}') -- \
  pg_dump -h $DB_HOST -U $DB_USERNAME -d $DB_NAME > backup.sql

# Upload to Azure Storage
az storage blob upload \
  --account-name financebackups \
  --container-name database-backups \
  --name backup-$(date +%Y%m%d).sql \
  --file backup.sql
```

## Clean Up

```bash
# Delete Helm release
helm uninstall finance-agent -n finance

# Delete namespace
kubectl delete namespace finance

# Delete Azure resources
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Cost Optimization

1. **Use Azure Reserved Instances** for AKS nodes
2. **Enable autoscaling** to scale down during low traffic
3. **Use Azure Spot VMs** for non-critical workloads
4. **Monitor costs** with Azure Cost Management

## Security Best Practices

1. ✅ Use Azure Key Vault for secrets
2. ✅ Enable Azure AD authentication
3. ✅ Use Network Policies
4. ✅ Enable Pod Security Standards
5. ✅ Regular security scanning
6. ✅ TLS/SSL for all traffic

---

**Deployment complete!** Your Personal Finance Agent is now running on Azure with Azure OpenAI! 🎉
