# Azure Setup

> These scripts will help setup the Azure deployment

## Prerequisites

- **[Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)**

### App Service

You can complete this using the Azure Portal or CLI.
The example will be using the Azure Portal (CLI Instuctions TBD)

> NOTE: The rest of this README will assume that you have experience with Azure

Create a web app with the following specifications:

**Basic**

| name             | value            |
| ---------------- | ---------------- |
| Publish          | Docker Container |
| Operating System | Linux            |

**Docker**

| name                    | value                                         | description                                |
| ----------------------- | --------------------------------------------- | ------------------------------------------ |
| Options                 | Single Container                              |                                            |
| Image Source            | Private Registry                              |                                            |
| Server URL              | `https://quay.io`                             |                                            |
| Username                |                                               | The username of the robot account for Quay |
| Password                |                                               | The token for the robot account for Quay   |
| Full Image Name and Tag | `nimbusinformatics/bdcat-data-tracker:latest` |                                            |

From here, you will need to go into "Deployment>Deployment Center" and turn on Continuous Deployment

### Azure Database for PostgreSQL

You will need to create a single-server database with the following specifications:

**Basics**

| name           | value      |
| -------------- | ---------- |
| Version        | 11         |
| Admin username | `postgres` |

> NOTE: This may take a several minutes

From here, you will need to go to "Settings>Connection security":

| name                   | value                             |
| ---------------------- | --------------------------------- |
| Firewall rule name     | Add `0.0.0.0` - `255.255.255.255` |
| Enforce SSL connection | DISABLED                          |

Take note of the "Admin username" and "Server name" as that will be your `POSTGRES_USER` and `POSTGRES_HOST` enviorment variables
