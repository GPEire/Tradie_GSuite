# Google Cloud Platform (GCP) Setup

## Overview

This project uses **Google Cloud Platform (GCP)** as the primary cloud infrastructure due to:
- Native integration with Google APIs (Gmail, Sheets, Drive)
- Seamless OAuth2 authentication
- Google Cloud Functions for serverless backend
- Firestore for scalable data storage
- Cost-effective for MVP and scale

## Infrastructure Components

### 1. Google Cloud Project

**Create a new GCP project:**
```bash
gcloud projects create tradie-gsuite --name="Tradie GSuite Email Extension"
gcloud config set project tradie-gsuite
```

**Enable required APIs:**
```bash
gcloud services enable gmail.googleapis.com
gcloud services enable sheets.googleapis.com
gcloud services enable drive.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Authentication & OAuth

**Create OAuth 2.0 credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Chrome Extension"
4. Application ID: Your Chrome Extension ID (get from Chrome Web Store developer dashboard)
5. Download credentials and store securely

**For web application (backend):**
1. Create another OAuth 2.0 client ID
2. Application type: "Web application"
3. Authorized redirect URIs:
   - `http://localhost:8000/auth/callback` (development)
   - `https://api.staging.example.com/auth/callback` (staging)
   - `https://api.production.example.com/auth/callback` (production)

### 3. Cloud Functions (Backend API)

**Deploy FastAPI backend as Cloud Functions:**

```bash
# Install Cloud Functions Framework
pip install functions-framework

# Deploy function
gcloud functions deploy email-grouping-api \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=./backend \
  --entry-point=app.main.app \
  --trigger=http \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLIENT_ID=...,GOOGLE_CLIENT_SECRET=..."
```

**Or use Cloud Run (recommended for FastAPI):**
```bash
gcloud run deploy email-grouping-api \
  --source=./backend \
  --region=us-central1 \
  --platform=managed \
  --allow-unauthenticated
```

### 4. Firestore Database

**Create Firestore database:**
```bash
gcloud firestore databases create \
  --location=us-central1 \
  --type=firestore-native
```

**Collections structure:**
- `users` - User profiles and settings
- `projects` - Project metadata
- `email_mappings` - Email to project associations
- `corrections` - User corrections for ML training
- `audit_logs` - Compliance and audit trail

### 5. Cloud Storage (Attachments)

**Create bucket for email attachments:**
```bash
gsutil mb -p tradie-gsuite -l us-central1 gs://tradie-email-attachments
```

**Set up lifecycle policies:**
```bash
gsutil lifecycle set lifecycle.json gs://tradie-email-attachments
```

### 6. Environment Configuration

**Set secrets in Secret Manager:**
```bash
# Store API keys securely
echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-anthropic-key" | gcloud secrets create anthropic-api-key --data-file=-
echo -n "your-secret-key" | gcloud secrets create secret-key --data-file=-
```

**Access secrets in Cloud Functions:**
```python
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/tradie-gsuite/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

## Deployment

### Development
```bash
# Local development with emulators
gcloud emulators firestore start
gcloud functions-framework --target=app.main.app --port=8080
```

### Staging
```bash
# Deploy to staging environment
gcloud run deploy email-grouping-api-staging \
  --source=./backend \
  --region=us-central1 \
  --env-vars-file=config/staging.env.yaml
```

### Production
```bash
# Deploy to production
gcloud run deploy email-grouping-api \
  --source=./backend \
  --region=us-central1 \
  --env-vars-file=config/production.env.yaml \
  --min-instances=1
```

## Cost Estimation

**MVP Scale (100 users):**
- Cloud Functions: ~$5-10/month
- Firestore: ~$10-20/month
- Cloud Storage: ~$1-5/month
- **Total: ~$20-35/month**

**Growth Scale (1,000 users):**
- Cloud Functions: ~$50-100/month
- Firestore: ~$100-200/month
- Cloud Storage: ~$10-20/month
- **Total: ~$160-320/month**

## Security Best Practices

1. **IAM Roles:** Use least privilege principle
2. **Secret Manager:** Never hardcode credentials
3. **VPC:** Use private networking for internal services
4. **Audit Logs:** Enable Cloud Audit Logs
5. **Encryption:** Enable encryption at rest and in transit

## Monitoring & Logging

**Set up monitoring:**
```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Create alerting policies
# Monitor: Function errors, API latency, quota usage
```

**View logs:**
```bash
gcloud functions logs read email-grouping-api --limit=50
```

## Next Steps

1. Set up GCP project and enable APIs
2. Configure OAuth credentials
3. Deploy backend to Cloud Run
4. Set up Firestore database
5. Configure environment variables and secrets
6. Set up CI/CD for automated deployments

