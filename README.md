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