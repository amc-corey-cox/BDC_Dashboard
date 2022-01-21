# Postgres Database Setup

> These ansible scripts will help setup the Postgres database on a Compute Engine instance.

## Prerequisites

- **[Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)**
- **GCP Compute Engine Instance w/ [Persistent Disk Mounted](https://cloud.google.com/compute/docs/disks/add-persistent-disk#mounting)**
  - These scripts have been tested on a VM with Ubuntu 20.04.3 LTS with a 10GB mounted disk

### `inventory`

The `inventory` file is an INI file that is missing two required sections: `ansible_user` and `ansible_host`:

| name           | value    | description                                       |
| -------------- | -------- | ------------------------------------------------- |
| `ansible_user` | `ubuntu` | The registered user within the VM                 |
| `ansible_host` |          | The IP address of the GCP Compute Engine Instance |

### `/group_vars/all`

There should be two `yml` files in the `group_vars/all` directory.

In the `users.yml` file, please add your public SSH key to the `authorized_keys` list

In the `nimbus.yml` file, please define the following variables:

| name            | value             | description                                                      |
| --------------- | ----------------- | ---------------------------------------------------------------- |
| `db_dir`        | `/opt/bdcat`      | The directory where the `docker-compose` image will be stored    |
| `db_data_dir`   | `/tickets`        | The directory where the Postgres database will be stored         |
| `db_backup_dir` | `/tickets_backup` | The directory where the Postgres database backups will be stored |

### `/templates`

This directory should have an `.env` file with the following:

| name                | value             | description                                               |
| ------------------- | ----------------- | --------------------------------------------------------- |
| `BDCAT_DATA_DIR`    | `{{db_data_dir}}` | A reference to the `db_data_dir` in the `nimbus.yml` file |
| `POSTGRES_DB`       | `tickets`         | The Postgres database name                                |
| `POSTGRES_USER`     | `postgres`        | The username of the Postgres User                         |
| `POSTGRES_PASSWORD` |                   | The password for the Postgres User                        |

## Deployment

After properly configuring the VM and directories, you can deploy the Postgres database into the VM

```
ansible-playbook -i inventory setup.yml
```

After the setup is complete, you can deploy the Postgres Docker image into the VM

```
ansible-playbook -i inventory deploy-pg.yml
```

You must migrate the Django database into the Postgres database

```
cd ../api
python manage.py migrate
```

You can now connect to the Postgres database using the Django app!
