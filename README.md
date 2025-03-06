# cloudsecitw

 req
 Authenticate with Google Cloud
gcloud auth login

 Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required services
cloud services enable \
  aiplatform.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com


#  Setup Guide
1. Initial Setup

# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Clone  project
git clone [https://github.com/hawikk/cloudsecitw]
cd cloud-security-analyzer


2. Enable Required APIs

gcloud services enable \
  aiplatform.googleapis.com \
  appengine.googleapis.com \
  cloudbuild.googleapis.com


3. Service Account Setup

# Get your project number
PROJECT_NUMBER=$(gcloud projects describe $GOOGLE_CLOUD_PROJECT --format='value(projectNumber)')

# Assign Vertex AI permissions
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
  --role=roles/aiplatform.user


4. Configure Environment

# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"

# Update requirements
pip install -r requirements.txt


5. Deployment
App Engine 

# Deploy to App Engine
gcloud app deploy --project=$GOOGLE_CLOUD_PROJECT

# After deployment, open in browser
gcloud app browse

