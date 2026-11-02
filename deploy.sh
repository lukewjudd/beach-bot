#!/usr/bin/env bash
# Deploys the beach bot as a Cloud Run Job, run by Cloud Scheduler at 4am, 3pm and 7pm Sydney time.
# Safe to re-run: it updates whatever already exists.
#
# Settings come from .env (PROJECT_ID, CALENDAR_ID) or the environment:
#   ./deploy.sh
set -euo pipefail
cd "$(dirname "$0")"
[[ -f .env ]] && { set -a; source .env; set +a; }
# Always use the personal gcloud profile, whatever is active in the shell
export CLOUDSDK_ACTIVE_CONFIG_NAME=${GCLOUD_CONFIG:-beach}

PROJECT=${PROJECT:-${PROJECT_ID:?set PROJECT_ID in .env to your personal Google Cloud project id}}
CALENDAR_ID=${CALENDAR_ID:?set CALENDAR_ID to the Beach calendar id}
REGION=${REGION:-us-central1}   # free tier region; the schedule still runs on Sydney time
SA_NAME=beach-bot
SA="$SA_NAME@$PROJECT.iam.gserviceaccount.com"
BUCKET="$PROJECT-beach-scores"   # public: holds scores.json for the map site

ACCOUNT=$(gcloud config get-value account 2>/dev/null)
echo "Deploying to project '$PROJECT' as $ACCOUNT"
g() { gcloud --project "$PROJECT" --quiet "$@"; }

echo "→ Enabling APIs"
g services enable run.googleapis.com cloudscheduler.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com calendar-json.googleapis.com

echo "→ Service account"
g iam service-accounts describe "$SA" >/dev/null 2>&1 \
  || g iam service-accounts create "$SA_NAME" --display-name "Beach bot"

echo "→ Build permissions"
# New projects build as the compute default account, which starts with no rights to build
NUMBER=$(g projects describe "$PROJECT" --format "value(projectNumber)")
g projects add-iam-policy-binding "$PROJECT" --condition None \
  --member "serviceAccount:$NUMBER-compute@developer.gserviceaccount.com" --role roles/run.builder >/dev/null

echo "→ Public scores bucket"
g storage buckets describe "gs://$BUCKET" >/dev/null 2>&1 \
  || g storage buckets create "gs://$BUCKET" --location "$REGION" --uniform-bucket-level-access
g storage buckets add-iam-policy-binding "gs://$BUCKET" --member allUsers --role roles/storage.objectViewer >/dev/null
g storage buckets add-iam-policy-binding "gs://$BUCKET" --member "serviceAccount:$SA" --role roles/storage.objectAdmin >/dev/null
CORS=$(mktemp)
echo '[{"origin": ["*"], "method": ["GET"], "responseHeader": ["Content-Type"], "maxAgeSeconds": 3600}]' > "$CORS"
g storage buckets update "gs://$BUCKET" --cors-file "$CORS" >/dev/null
rm "$CORS"

echo "→ Building and deploying the job"
g run jobs deploy beach-bot --source . --region "$REGION" \
  --service-account "$SA" --set-env-vars "BEACH_CALENDAR_ID=$CALENDAR_ID,BEACH_BUCKET=$BUCKET" \
  --max-retries 1 --task-timeout 300

g run jobs add-iam-policy-binding beach-bot --region "$REGION" \
  --member "serviceAccount:$SA" --role roles/run.invoker >/dev/null

echo "→ Schedule"
SCHED=(--location "$REGION" --schedule "0 4,15,19 * * *" --time-zone "Australia/Sydney"
  --uri "https://run.googleapis.com/v2/projects/$PROJECT/locations/$REGION/jobs/beach-bot:run"
  --http-method POST --oauth-service-account-email "$SA")
g scheduler jobs create http beach-bot-schedule "${SCHED[@]}" 2>/dev/null \
  || g scheduler jobs update http beach-bot-schedule "${SCHED[@]}"

echo
echo "Done. Share the Beach calendar with $SA (Make changes to events), then test it:"
echo "  gcloud --project $PROJECT run jobs execute beach-bot --region $REGION --wait"
