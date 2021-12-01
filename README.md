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

### Roadmap

- [ ] Migrate DB to Postgres
  - [ ] Dockerize the Postgres DB
- [ ] Add admin panel
- [ ] Add deployment instructions
- [ ] Add tests(?)
