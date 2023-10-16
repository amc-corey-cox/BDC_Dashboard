# Postgres Database Setup

> These ansible scripts will help setup the Postgres database on a Compute Engine instance.

## Prerequisites

- **[Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)**
- **GCP Compute Engine Instance w/ [Persistent Disk Mounted](https://cloud.google.com/compute/docs/disks/add-persistent-disk#mounting)**
  - These scripts have been tested on a VM with Ubuntu 20.04.3 LTS with a 10GB mounted disk

### `inventory`

The [`inventory.example`](./inventory.example) file is an INI file that is missing two required sections: `ansible_user` and `ansible_host`:

| name           | value    | description                                       |
| -------------- | -------- | ------------------------------------------------- |
| `ansible_user` | `ubuntu` | The registered user within the VM                 |
| `ansible_host` |          | The IP address of the GCP Compute Engine Instance |

After filling in the required fields, remove the `.example` extension and save the file as `inventory`.

### [`/group_vars/all`](./group_vars/all)

There should be two `yml` files in the `group_vars/all` directory.

In the [`users.yml.example`](./group_vars/all/users.yml.example) file, please add your public SSH key to the `authorized_keys` list.
After adding your public key, remove the `.example` extension and save the file as `users.yml`.

In the [`nimbus.yml`](./group_vars/all/nimbus.yml) file, please define the following variables:

| name          | value         | description                                                   |
| ------------- | ------------- | ------------------------------------------------------------- |
| `db_dir`      | `/opt/bdcat`  | The directory where the `docker-compose` image will be stored |
| `db_data_dir` | `/bdcat/data` | The directory where the Postgres database will be stored      |

### [`/templates`](./templates)

This directory should have an `.env` file with the following:

| name                | value             | description                                               |
| ------------------- | ----------------- | --------------------------------------------------------- |
| `POSTGRES_DATA_DIR` | `{{db_data_dir}}` | A reference to the `db_data_dir` in the `nimbus.yml` file |
| `POSTGRES_DB`       | `tickets`         | The Postgres database name                                |
| `POSTGRES_USER`     | `postgres`        | The username of the Postgres User                         |
| `POSTGRES_PASSWORD` |                   | The password for the Postgres User                        |

### Remote Access

Due to the nature of how GCP works, some manual steps are required to allow there ansible scripts to access the VM.

Use the GCP Console to SSH into the VM. Once connected, you must add your public SSH key to the `ubuntu` user's `authorized_keys` file:

```
sudo su
cd /home/ubuntu/.ssh
nano authorized_keys
```

Paste the ssh key used in the `users.yml` file into the `authorized_keys` file.
Ensure that your local machine is able to access the VM via SSH:

```
cd ~/.ssh
ssh -i id_rsa ubuntu@0.0.0.0
```

> NOTE: You should replace `id_rsa` with the name of your private key and `0.0.0.0` with the external IP of the VM

## Deployment

After properly configuring the VM and directories, you can deploy the Postgres database into the VM

### Ansible

```
ansible-playbook -i inventory setup.yml
```

After the setup is complete, you can deploy the Postgres Docker image into the VM

```
ansible-playbook -i inventory deploy-pg.yml
```

The Postgres database should now be running on the VM.

### VM Configuration

Ensure the docker container is running in the VM:

```
sudo su
docker ps
```

You must set a password for the `postgres` user:

```
docker exec -it bdcat_database_1 psql -U postgres
```

> NOTE: You may also need to replace `bdcat_database_1` with the name of the docker container

Once inside the container you should see the following:

```
psql (14.1)
Type "help" for help.

postgres=#
```

Change the password for the user `postgres`:

```
ALTER USER postgres WITH PASSWORD 'password';
```

Make sure you replace `password` with a (secure) password you set in the [`api/.env`](/.env) file

> NOTE: If using another user, change `postgres` with the user set in the [`api/.env`](/.env) file

On your local machine, you must migrate the Django model into the Postgres database:

```
python manage.py makemigrations
python manage.py migrate
```

#### Persistent Disk Mount

Docker containers are volitile and do not retain state between runs.
This means that if the container restarts, the database will be lost.
To mitigate this, you must mount a persistent disk to the VM and bind that to the container's `/tickets` volume

Make sure that a `sdb` block device with the correct size is attached to the VM:

```
sudo su
lsblk
```

Format the `sdb` block device to `ext4`:

```
mkfs.ext4 -m 0 -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/sdb
```

> NOTE: You may change some of the flags, but these are the Google recommended settings

Mount the newly formatted `sdb` block device to the `/tickets` directory:

```
mount -o discard,defaults /dev/sdb /tickets
chmod a+w /tickets
```

#### Reserving a Static IP

When the VM goes down, the IP address will be released.
[To prevent this, you must reserve a static IP address for the VM](https://cloud.google.com/compute/docs/ip-addresses/reserve-static-external-ip-address#reserve_new_static)

> NOTE: The cost of a static IP is [$0.004/hour](https://cloud.google.com/vpc/network-pricing)

If you do not want a static IP, you must monitor the VM for its status and change the IP configuration if the IP changes

### Failsafe(s)

#### Monitoring

You can set up monitoring for the VM for errors and other events using [Google's Ops Agent](https://cloud.google.com/stackdriver/docs/solutions/agents/ops-agent/installation#gce-ui-install)

You will need the [`roles/monitoring.admin`](https://cloud.google.com/iam/docs/understanding-roles#monitoring-roles) to create monitoring alerts

#### VM Reboot Configuration

If the VM goes down, you must remount the the block device.
Alternatively, you can [configure automatic mounting on reboot](https://cloud.google.com/compute/docs/disks/add-persistent-disk#configuring_automatic_mounting_on_vm_restart)

#### Snapshots

The persistent disk mount will prevent the database from being wiped if the docker container is restarted.
You must also [add a failsafe snapshot to the persistent disk](https://cloud.google.com/compute/docs/disks/scheduled-snapshots) to prevent data loss

##### Restoring from Snapshot

In the case that data is corrupted, [you can restore from a snapshot](https://cloud.google.com/compute/docs/disks/create-snapshots#restore-snapshots).
If your container is working fine, you will only need to attach the restored persistent disk

If the VM is corrupted, you will only need to rebuild the container and attach the same persistent disk

> NOTE: These steps have not been formally tested

### Limitations

These scripts are only for initial deployment and will not act on existing deployments.

**If any issues arise, you must manually resolve them in the VM**
