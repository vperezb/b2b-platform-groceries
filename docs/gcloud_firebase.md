# Google Cloud

1. Create service credentials within your project
2. Create a forlder and a virtualenv from a requirements file
2. Set environment var using `set GOOGLE_APPLICATION_CREDENTIALS=[PATH]`, `export GOOGLE_APPLICATION_CREDENTIALS=[PATH]`

`gcloud auth activate-service-account sandbox-product@aaaojects.iam.gserviceaccount.com --key-file="C:/Users/myuser/.credentials/aaaojects-58bfac812e72.json"`

## App Engine

`gcloud app deploy dispatch.yaml`

`gcloud auth application-default login`

`gcloud datastore indexes create index.yaml`

`gcloud datastore indexes cleanup index.yaml`

https://cloud.google.com/appengine/docs/standard/python/datastore/queries

https://cloud.google.com/solutions/big-data


## Storage

https://googleapis.dev/python/storage/latest/blobs.html
https://cloud.google.com/storage/docs/json_api/v1/objects
https://www.iana.org/assignments/media-types/media-types.xhtml
`$ export GOOGLE_APPLICATION_CREDENTIALS="C:/Users/User/Documents/blabla.json"`
https://medium.com/google-developers/building-a-simple-web-upload-interface-with-google-cloud-run-and-cloud-storage-eba0a97edc7b


## Datastore

https://stackoverflow.com/questions/11328412/gae-gql-get-entity-if-list-contains-item

https://cloud.google.com/blog/products/storage-data-transfer/uploading-images-directly-to-cloud-storage-by-using-signed-url

## PubSub

Publish and consume plain text messages

gcloud pubsub topics create statistics
gcloud pubsub subscriptions create almarcat --topic statistics --ack-deadline=60
gcloud pubsub topics list
gcloud pubsub subscriptions list
gcloud pubsub topics publish statistics --message hello
gcloud pubsub topics publish statistics --message thanks
gcloud pubsub subscriptions pull --auto-ack --limit=2 almarcat
gcloud pubsub subscriptions pull almarcat
gcloud pubsub subscriptions ack almarcat --ack-ids ACK_ID

## Gsutil

https://cloud.google.com/storage/docs/configuring-cors
gsutil cors set configs/cors.json gs://aa-local

# Firebase

https://github.com/firebase/firebaseui-web