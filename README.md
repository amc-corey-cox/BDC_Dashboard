# BioData Catalyst Tracker

> A web-based data tracker for submission process

## Getting started

### Prerequisites

- **[Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)**
- **[Docker](https://www.docker.com/get-started)**
- **[Cloud SDK CLI](https://cloud.google.com/sdk/gcloud)**

### Environment variables

For local development, the `api` directory should have an `.env` file with the following:

| name                 | value      | description                                                   |
| -------------------- | ---------- | ------------------------------------------------------------- |
| GOOGLE_CLOUD_PROJECT |            | The Project ID for GCP                                        |
| SECRET_KEY           |            | The `SECRET_KEY` generated by Django                          |
| POSTGRES_DB          | `tickets`  | The Postgres database name                                    |
| POSTGRES_USER        | `postgres` | The username of the Postgres User                             |
| POSTGRES_PASSWORD    |            | A (secure) password for the Postgres User                     |
| POSTGRES_HOST        |            | The external IP for the Compute Engine instance with Postgres |
| POSTGRES_PORT        | `5432`     | The port for the Postgres Database                            |

> NOTE: If the Compute Engine instance restarts and the IP changes, you must update the `POSTGRES_HOST` variable

### The Postgres Database

Due to the complexity of the setup, we have included some Ansible Playbooks to assist you.
You can find a detailed writeup in the [`ansible`](/ansible) directory

> NOTE: This is required even for local development

### The Django Server

Docker Compose should start a Django server on [`http://0.0.0.0:8000/`](http://0.0.0.0:8000/).
The server uses the `env` file for configuration

### Docker Compose

Docker is used to standardize the development environment

```
docker-compose up --build
```

> NOTE: This may take a several minutes

You should only need to build this once (or when you make changes to the `Dockerfile` or `docker-compose.yml`).
Any subsequent runs do not require the `--build` flag:

```
docker-compose up
```

## Deployment

We will be using [this guide to deploy to App Engine](https://cloud.google.com/python/django/appengine#macos-64-bit)

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

To prepare the project for deployment, run the following commands:

```
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate
```

#### [Secrets Manager](https://cloud.google.com/python/django/appengine#create-django-environment-file-as-a-secret)

In GCP Secret Manager, you must create a secret called `django_settings`.
You can either upload the `.env` file or paste the secrets in there

> NOTE: If the Compute Engine instance restarts and the IP changes, you must update the `POSTGRES_HOST` variable

#### App Engine

This repo has been configured to use GitHub Actions to deploy to App Engine on pushes to the `main` branch.
For this to work, you must have GitHub Secrets with the following:

| name       | description                                         |
| ---------- | --------------------------------------------------- |
| PROJECT_ID | The Project ID for GCP                              |
| GCP_SA_KEY | The full service account key json exported from GCP |

Alternatively, can navigate to the `api` directory and run:

```
gcloud app deploy
```

#### Limitations

If the Compute Engine instance restarts, there may be a change in the IP address.

**If this is the case, you must update the `.env` file for local deployment and the `django_settings` secret on GCP**
