# BioData Catalyst Tracker

> A web-based data tracker for submission process

## Getting started

### Prerequisites

- **[Docker](https://www.docker.com/get-started)**
- **[Cloud SDK CLI](https://cloud.google.com/sdk/gcloud)**
- A [service account key](https://cloud.google.com/iam/docs/creating-managing-service-account-keys#creating) for the "App Engine default service account"
  - This file should be named `service_account.json` and placed in the **root** of the project
  - You may use a custom service account key if you wish, but this has not been tested

### Environment variables

For local development, you must create two `.env` files. In the **root** of the project the `.env` file should contain the following:

| name                    | value | description                     |
| ----------------------- | ----- | ------------------------------- |
| GOOGLE_CLOUD_PROJECT    |       | The Project ID for GCP          |
| CLOUD_SQL_REGION        |       | The region for Cloud SQL        |
| CLOUD_SQL_INSTANCE_NAME |       | The instance name for Cloud SQL |

In the `api` directory the `.env` file must also contain the following:

| name                     | value                                                                                                           | description                                                                                              |
| ------------------------ | --------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| USE_CLOUD_SQL_AUTH_PROXY | `True`                                                                                                          |                                                                                                          |
| GOOGLE_CLOUD_PROJECT     |                                                                                                                 | The Project ID for GCP                                                                                   |
| DATABASE_URL             | `postgres://$DATABASE_USERNAME:$DATABASE_PASSWORD@//cloudsql/$PROJECT_ID:$REGION:$INSTANCE_NAME/$DATABASE_NAME` |                                                                                                          |
| GS_BUCKET_NAME           | `$PROJECT_ID_$MEDIA_BUCKET`                                                                                     |                                                                                                          |
| SECRET_KEY               |                                                                                                                 | [Reference](https://cloud.google.com/python/django/appengine#create-django-environment-file-as-a-secret) |

### Docker Compose

Docker is used to standardize the development enviornment. Since deployment will be on App Engine, Docker Compose is used to manage the different services. The Dockerfile and Docker Compose file will not be used in production

With the Docker Daemon running, navigate to the project root directory and run:

```
docker-compose up --build
```

This will spin up a Docker container to serve the app

> NOTE: This may take a several minutes

You should only need to build this once (or when you make changes to the `Dockerfile`).
Any subsequent runs do not require the `--build` flag

```
docker-compose up
```

### Cloud SQL Proxy

Since we are using Google's Cloud SQL as a database, you must use the Cloud SQL Proxy client
![Cloud SQL Proxy to Cloud SQL](https://cloud.google.com/sql/images/proxyconnection.svg)

This is automatically configured for you when you run `docker-compose up` and uses the service account key provided in the `service_account.json` file

### The Django Server

Docker Compose should start a Django server on [`http://0.0.0.0:8000/`](http://0.0.0.0:8000/).
The server is configured to serve the web app so no further configuration is needed

## Deployment

We will be using [this guide to deploy GCP](https://cloud.google.com/python/django/appengine#macos-64-bit)

### [Permissions](https://cloud.google.com/iam/docs/understanding-roles#predefined)

- [`roles/appengine.appAdmin`](https://cloud.google.com/iam/docs/understanding-roles#app-engine-roles)
- [`roles/cloudbuild.integrationsOwner`](https://cloud.google.com/iam/docs/understanding-roles#cloud-build-roles)
- [`roles/cloudbuild.builds.editor`](https://cloud.google.com/build/docs/iam-roles-permissions#predefined_roles)
- [`roles/cloudsql.admin`](https://cloud.google.com/iam/docs/understanding-roles#cloud-sql-roles)
- [`roles/secretmanager.admin`](https://cloud.google.com/iam/docs/understanding-roles#secret-manager-roles)
- [`roles/iam.serviceAccountAdmin`](https://cloud.google.com/iam/docs/understanding-roles#service-accounts-roles)
- [`roles/serviceusage.serviceUsageAdmin`](https://cloud.google.com/iam/docs/understanding-roles#service-usage-roles)
- [`roles/storage.admin`](https://cloud.google.com/iam/docs/understanding-roles#cloud-storage-roles)

> NOTE: you will also need to grant yourself the [`roles/iam.serviceAccountUser`](https://cloud.google.com/iam/docs/understanding-roles#service-accounts-roles) on the `App Engine default service account`

### Instructions

**Ensure all prior setup is complete before continuing**

Navigate to the `api` directory and run:

```
gcloud app deploy
```

> NOTE: You must have the Cloud SDK CLI installed and configured to use the `gcloud` command
