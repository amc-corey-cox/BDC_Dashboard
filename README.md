# BioData Catalyst Tracker

> A web-based data tracker for submission process

## Getting started

### Prerequisites

- **[Docker](https://www.docker.com/get-started)**
- Inside the `api` directory, you need 2 files
  - `.env` with the value `SECRET_KEY`
  - `db.sqlite3` file for the database

### Docker Compose

With the Docker Daemon running, navigate to the project root directory and run:

```
docker-compose up --build
```

This will spin up a Docker container to serve the app

> NOTE: This may take a few minutes

You should only need to build this once (or when you make changes to the `Dockerfile`).
Any subsequent runs do not require the `--build` flag

```
docker-compose up
```

### The Django Server

Docker compose should start a Django server on [`http://0.0.0.0:8000/`](http://0.0.0.0:8000/).
The server is configured to serve the web app so no further configuration is needed

## Deployment

We will be using [this guide to deploy GCP](https://cloud.google.com/python/django/appengine#macos-64-bit)

### [Permissions](https://cloud.google.com/iam/docs/understanding-roles#predefined)

- [`roles/appengine.appAdmin`](https://cloud.google.com/iam/docs/understanding-roles#app-engine-roles)
- [`roles/cloudbuild.integrationsOwner`](https://cloud.google.com/iam/docs/understanding-roles#cloud-build-roles)
- [`roles/cloudsql.admin`](https://cloud.google.com/iam/docs/understanding-roles#cloud-sql-roles)
- [`roles/secretmanager.admin`](https://cloud.google.com/iam/docs/understanding-roles#secret-manager-roles)
- [`roles/iam.serviceAccountAdmin`](https://cloud.google.com/iam/docs/understanding-roles#service-accounts-roles)
- [`roles/serviceusage.serviceUsageAdmin`](https://cloud.google.com/iam/docs/understanding-roles#service-usage-roles)
- [`roles/storage.admin`](https://cloud.google.com/iam/docs/understanding-roles#cloud-storage-roles)

> NOTE: you will also need to grant yourself the [`roles/iam.serviceAccountUser`](https://cloud.google.com/iam/docs/understanding-roles#service-accounts-roles) on the `App Engine default service account`
