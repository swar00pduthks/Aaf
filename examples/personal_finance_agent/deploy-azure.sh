#!/bin/bash

set -e

echo "=================================="
echo "Azure Deployment Script"
echo "=================================="
echo ""

# Configuration
RESOURCE_GROUP="${RESOURCE_GROUP:-finance-agent-rg}"
LOCATION="${LOCATION:-eastus}"
AKS_NAME="${AKS_NAME:-finance-aks}"
ACR_NAME="${ACR_NAME:-financeagentacr}"
OPENAI_NAME="${OPENAI_NAME:-finance-openai}"
DB_SERVER_NAME="${DB_SERVER_NAME:-finance-db-server}"
REDIS_NAME="${REDIS_NAME:-finance-cache}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

# Step 1: Verify Azure CLI
print_step "Verifying Azure CLI installation..."
if ! command -v az &> /dev/null; then
    echo "Azure CLI not found. Please install it first."
    exit 1
fi
print_success "Azure CLI found"

# Step 2: Login to Azure
print_step "Logging in to Azure..."
az login
print_success "Logged in to Azure"

# Step 3: Create Resource Group
print_step "Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION \
    --output table
print_success "Resource group created"

# Step 4: Create ACR
print_step "Creating Azure Container Registry..."
az acr create \
    --resource-group $RESOURCE_GROUP \
    --name $ACR_NAME \
    --sku Standard \
    --output table

az acr update \
    --name $ACR_NAME \
    --admin-enabled true
print_success "ACR created"

# Get ACR credentials
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer --output tsv)
print_success "ACR Login Server: $ACR_LOGIN_SERVER"

# Step 5: Build and Push Docker Images
print_step "Building and pushing Docker images..."

# Login to ACR
az acr login --name $ACR_NAME

# Build backend
print_step "Building backend image..."
docker build -t $ACR_LOGIN_SERVER/finance-backend:1.0.0 -f Dockerfile.backend .
docker push $ACR_LOGIN_SERVER/finance-backend:1.0.0
print_success "Backend image pushed"

# Build frontend
print_step "Building frontend image..."
docker build -t $ACR_LOGIN_SERVER/finance-frontend:1.0.0 -f frontend/Dockerfile.frontend ./frontend
docker push $ACR_LOGIN_SERVER/finance-frontend:1.0.0
print_success "Frontend image pushed"

# Step 6: Create AKS Cluster
print_step "Creating AKS cluster (this may take 10-15 minutes)..."
az aks create \
    --resource-group $RESOURCE_GROUP \
    --name $AKS_NAME \
    --node-count 3 \
    --node-vm-size Standard_D4s_v3 \
    --enable-addons monitoring \
    --enable-managed-identity \
    --attach-acr $ACR_NAME \
    --generate-ssh-keys \
    --output table
print_success "AKS cluster created"

# Get AKS credentials
az aks get-credentials --resource-group $RESOURCE_GROUP --name $AKS_NAME --overwrite-existing
print_success "AKS credentials configured"

# Step 7: Create Azure OpenAI
print_step "Creating Azure OpenAI service..."
az cognitiveservices account create \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --kind OpenAI \
    --sku S0 \
    --location $LOCATION \
    --output table

AZURE_OPENAI_ENDPOINT=$(az cognitiveservices account show \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query properties.endpoint --output tsv)

AZURE_OPENAI_API_KEY=$(az cognitiveservices account keys list \
    --name $OPENAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query key1 --output tsv)

print_success "Azure OpenAI created"
print_warning "IMPORTANT: Create GPT-4 and GPT-3.5 deployments in Azure OpenAI Studio"
print_warning "Visit: https://oai.azure.com"

# Step 8: Create PostgreSQL
print_step "Creating Azure Database for PostgreSQL..."
DB_USERNAME="financeadmin"
DB_PASSWORD=$(openssl rand -base64 32)

az postgres flexible-server create \
    --resource-group $RESOURCE_GROUP \
    --name $DB_SERVER_NAME \
    --location $LOCATION \
    --admin-user $DB_USERNAME \
    --admin-password "$DB_PASSWORD" \
    --sku-name Standard_D2s_v3 \
    --tier GeneralPurpose \
    --storage-size 128 \
    --version 14 \
    --output table

az postgres flexible-server db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $DB_SERVER_NAME \
    --database-name finance_db

DB_HOST="${DB_SERVER_NAME}.postgres.database.azure.com"
DATABASE_URL="postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:5432/finance_db?sslmode=require"
print_success "PostgreSQL created"

# Step 9: Create Redis
print_step "Creating Azure Cache for Redis..."
az redis create \
    --resource-group $RESOURCE_GROUP \
    --name $REDIS_NAME \
    --location $LOCATION \
    --sku Standard \
    --vm-size c1 \
    --output table

REDIS_HOST=$(az redis show --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query hostName --output tsv)
REDIS_PASSWORD=$(az redis list-keys --name $REDIS_NAME --resource-group $RESOURCE_GROUP --query primaryKey --output tsv)
print_success "Redis created"

# Step 10: Create Kubernetes Secrets
print_step "Creating Kubernetes secrets..."

kubectl create namespace finance --dry-run=client -o yaml | kubectl apply -f -

# ACR secret
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username --output tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query passwords[0].value --output tsv)

kubectl create secret docker-registry acr-secret \
    --docker-server=$ACR_LOGIN_SERVER \
    --docker-username=$ACR_USERNAME \
    --docker-password=$ACR_PASSWORD \
    --namespace=finance \
    --dry-run=client -o yaml | kubectl apply -f -

# Azure OpenAI secret
kubectl create secret generic azure-openai-secret \
    --from-literal=AZURE_OPENAI_API_KEY=$AZURE_OPENAI_API_KEY \
    --namespace=finance \
    --dry-run=client -o yaml | kubectl apply -f -

# Database secret
kubectl create secret generic postgres-secret \
    --from-literal=username=$DB_USERNAME \
    --from-literal=password="$DB_PASSWORD" \
    --from-literal=url="$DATABASE_URL" \
    --namespace=finance \
    --dry-run=client -o yaml | kubectl apply -f -

# Redis secret
kubectl create secret generic redis-secret \
    --from-literal=password=$REDIS_PASSWORD \
    --namespace=finance \
    --dry-run=client -o yaml | kubectl apply -f -

print_success "Secrets created"

# Step 11: Install NGINX Ingress
print_step "Installing NGINX Ingress Controller..."
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
    --dry-run=client -o yaml | kubectl apply -f - || true

print_success "NGINX Ingress installed"

# Step 12: Deploy Application with Helm
print_step "Deploying application..."

# Update values.yaml with actual values
cat > helm/personal-finance-agent/values-prod.yaml <<EOF
backend:
  image:
    repository: $ACR_LOGIN_SERVER/finance-backend
    tag: "1.0.0"

frontend:
  image:
    repository: $ACR_LOGIN_SERVER/finance-frontend
    tag: "1.0.0"

azureOpenAI:
  endpoint: "$AZURE_OPENAI_ENDPOINT"

database:
  host: "$DB_HOST"

redis:
  azure:
    host: "$REDIS_HOST"
EOF

# Install with Helm
helm upgrade --install finance-agent ./helm/personal-finance-agent \
    --namespace finance \
    --values ./helm/personal-finance-agent/values-prod.yaml \
    --wait

print_success "Application deployed"

# Step 13: Get Ingress IP
print_step "Waiting for Ingress IP..."
sleep 30
INGRESS_IP=$(kubectl get svc -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
print_success "Ingress IP: $INGRESS_IP"

# Summary
echo ""
echo "=================================="
echo "Deployment Complete!"
echo "=================================="
echo ""
echo "Resource Summary:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  AKS Cluster: $AKS_NAME"
echo "  ACR: $ACR_LOGIN_SERVER"
echo "  Azure OpenAI: $AZURE_OPENAI_ENDPOINT"
echo "  Database: $DB_HOST"
echo "  Redis: $REDIS_HOST"
echo "  Ingress IP: $INGRESS_IP"
echo ""
echo "Next Steps:"
echo "  1. Create Azure OpenAI deployments:"
echo "     - Visit: https://oai.azure.com"
echo "     - Create: gpt-4-deployment"
echo "     - Create: gpt-35-turbo-deployment"
echo ""
echo "  2. Configure DNS:"
echo "     - Create A record pointing to: $INGRESS_IP"
echo ""
echo "  3. Access application:"
echo "     - kubectl get pods -n finance"
echo "     - kubectl logs -n finance -l app.kubernetes.io/component=backend"
echo ""
echo "Credentials saved to: ./deployment-credentials.txt"
echo ""

# Save credentials
cat > deployment-credentials.txt <<EOF
Azure Deployment Credentials
============================

Resource Group: $RESOURCE_GROUP
Location: $LOCATION

ACR:
  Server: $ACR_LOGIN_SERVER
  Username: $ACR_USERNAME
  Password: $ACR_PASSWORD

Azure OpenAI:
  Endpoint: $AZURE_OPENAI_ENDPOINT
  API Key: $AZURE_OPENAI_API_KEY

Database:
  Host: $DB_HOST
  Username: $DB_USERNAME
  Password: $DB_PASSWORD
  Connection String: $DATABASE_URL

Redis:
  Host: $REDIS_HOST
  Password: $REDIS_PASSWORD

Ingress IP: $INGRESS_IP
EOF

chmod 600 deployment-credentials.txt

echo "=================================="
