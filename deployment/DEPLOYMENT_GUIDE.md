# AAF Deployment Guide for Azure Kubernetes Service (AKS)

This guide shows how to deploy AAF to Azure Kubernetes Service for production use.

## Prerequisites

- Azure CLI installed (`az cli`)
- Docker installed
- kubectl installed
- An Azure subscription
- Azure Container Registry (ACR) or Docker Hub account

## Option 1: Quick Deploy with AKS Automatic (Recommended)

### Step 1: Create AKS Automatic Cluster

```bash
# Set variables
export RESOURCE_GROUP="aaf-production"
export CLUSTER_NAME="aaf-cluster"
export LOCATION="eastus"
export ACR_NAME="aafregistry"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create ACR
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic

# Create AKS Automatic cluster (best practices built-in)
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --tier automatic \
  --enable-addons monitoring \
  --attach-acr $ACR_NAME \
  --generate-ssh-keys
```

### Step 2: Build and Push Docker Image

```bash
# Login to ACR
az acr login --name $ACR_NAME

# Build image
docker build -t $ACR_NAME.azurecr.io/aaf:v1.0 -f deployment/Dockerfile .

# Push to ACR
docker push $ACR_NAME.azurecr.io/aaf:v1.0
```

### Step 3: Deploy to Kubernetes

```bash
# Get cluster credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $CLUSTER_NAME

# Update deployment with your ACR name and image tag
export IMAGE_TAG="v1.0"
envsubst < deployment/kubernetes/deployment.yaml | kubectl apply -f -

# Apply horizontal pod autoscaler
kubectl apply -f deployment/kubernetes/hpa.yaml

# Check deployment status
kubectl get pods
kubectl get services

# Get external IP
kubectl get service aaf-api-service
```

## Option 2: Deploy with Helm (Advanced)

### Create Helm Chart

```bash
# Create helm chart structure
helm create aaf-chart

# Customize values.yaml with your settings
# Then install:
helm install aaf-release ./aaf-chart \
  --set image.repository=$ACR_NAME.azurecr.io/aaf \
  --set image.tag=v1.0 \
  --namespace production \
  --create-namespace
```

## Option 3: CI/CD with GitHub Actions

Create `.github/workflows/deploy-aks.yaml`:

```yaml
name: Deploy to AKS

on:
  push:
    branches: [main]

env:
  REGISTRY: ${{ secrets.ACR_NAME }}.azurecr.io
  IMAGE_NAME: aaf
  CLUSTER_NAME: aaf-cluster
  RESOURCE_GROUP: aaf-production

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and push image
      run: |
        az acr login --name ${{ secrets.ACR_NAME }}
        docker build -t $REGISTRY/$IMAGE_NAME:${{ github.sha }} -f deployment/Dockerfile .
        docker push $REGISTRY/$IMAGE_NAME:${{ github.sha }}
    
    - name: Set up kubectl
      uses: azure/aks-set-context@v3
      with:
        resource-group: ${{ env.RESOURCE_GROUP }}
        cluster-name: ${{ env.CLUSTER_NAME }}
    
    - name: Deploy to AKS
      run: |
        export IMAGE_TAG=${{ github.sha }}
        export ACR_NAME=${{ secrets.ACR_NAME }}
        envsubst < deployment/kubernetes/deployment.yaml | kubectl apply -f -
        kubectl rollout status deployment/aaf-api
```

## Production Considerations

### 1. Secrets Management

Use Azure Key Vault instead of Kubernetes secrets:

```bash
# Enable Azure Key Vault Provider
az aks enable-addons \
  --addons azure-keyvault-secrets-provider \
  --name $CLUSTER_NAME \
  --resource-group $RESOURCE_GROUP

# Create Key Vault
az keyvault create \
  --name aaf-keyvault \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Add secrets
az keyvault secret set \
  --vault-name aaf-keyvault \
  --name session-secret \
  --value "your-secure-secret"
```

### 2. Monitoring

```bash
# Enable Application Insights
az monitor app-insights component create \
  --app aaf-insights \
  --location $LOCATION \
  --resource-group $RESOURCE_GROUP \
  --application-type web
```

### 3. Multi-Tenancy

For multi-tenant deployments:

```yaml
# tenant-a-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aaf-tenant-a
  namespace: tenant-a
spec:
  replicas: 2
  template:
    spec:
      nodeSelector:
        tenant: tenant-a
      tolerations:
      - key: "tenant"
        operator: "Equal"
        value: "tenant-a"
        effect: "NoSchedule"
      containers:
      - name: aaf
        image: ${ACR_NAME}.azurecr.io/aaf:${IMAGE_TAG}
        env:
        - name: TENANT_ID
          value: "tenant-a"
```

### 4. Cost Optimization

```bash
# Use spot instances for dev/test
az aks nodepool add \
  --resource-group $RESOURCE_GROUP \
  --cluster-name $CLUSTER_NAME \
  --name spotpool \
  --priority Spot \
  --eviction-policy Delete \
  --spot-max-price -1 \
  --enable-cluster-autoscaler \
  --min-count 1 \
  --max-count 3
```

## Accessing the Deployed Application

```bash
# Get the external IP
export SERVICE_IP=$(kubectl get service aaf-api-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Test the API
curl http://$SERVICE_IP/health

# Access Swagger UI
open http://$SERVICE_IP/docs
```

## Troubleshooting

### Check Logs

```bash
# Get pod logs
kubectl logs -l app=aaf --tail=100

# Stream logs
kubectl logs -f deployment/aaf-api
```

### Use AKS CLI Agent (AI-powered troubleshooting)

```bash
# Diagnose cluster issues
az aks agent "why are my pods in tenant-a namespace not starting?"

# Check networking
az aks agent "check connectivity from aaf-api pods to external services"
```

### Scale Manually

```bash
# Scale up for high traffic
kubectl scale deployment aaf-api --replicas=5

# Scale down
kubectl scale deployment aaf-api --replicas=2
```

## Cleanup

```bash
# Delete resources
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Next Steps

1. **Add Ingress Controller**: Use Azure Application Gateway or NGINX Ingress
2. **Enable HTTPS**: Use cert-manager for automatic TLS certificates
3. **Setup GitOps**: Use Flux or ArgoCD for declarative deployments
4. **Implement Blue-Green**: Use Flagger for progressive delivery
5. **Add Service Mesh**: Use Istio or Linkerd for advanced traffic management

## Resources

- [AKS Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [AKS Best Practices](https://docs.microsoft.com/en-us/azure/aks/best-practices)
- [Azure Monitor for AKS](https://docs.microsoft.com/en-us/azure/azure-monitor/containers/container-insights-overview)
