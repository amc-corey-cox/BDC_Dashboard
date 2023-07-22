# Introduction
This guide will provide instruction and information on setting up the development environment for the BioData Catalyst (BDC) Data Management Core (DMC) Data Submission Tracker (DST). This will include installing prerequisites, setting up a development environment, building the container, deploying to BioData Catalyst, running tests/linting, and information about contributing to development.
> At this point all installation is managed system-wide. I think this is a poor way to manage a development environment. I would prefer that we use an environmental encapsulation of some sort, such as poetry or pyenv. We will try to move towards some encapsulation after we have an initial working environment.

---
# Contributing to the Project
To contribute to the project, follow the steps outlined in the [Setup the Development Environment](#setup-the-development-environment) section to create a local development environment. Once your environment is set up, you can make changes to the codebase and submit pull requests for review. If you encounter any issues during the setup process or while working on the project please submit an issue and describe the steps you are having trouble with.

---
# Setup the Development Environment
The steps necessary to set up the development are fairly  involved. First we will need to satisfy the [Prerequisites](#prerequisites), including [Dependancies](#dependancies), [Optional Dependancies](#optional-dependancies), and [Provision PostgreSQL VM on GCP](#provision-postgresql-vm-on-gcp). Please follow these instructions to properly setup and verify a functioning development environment.

## Prerequisites
In order to build and run the Data Submisison tracker several dependancies will need to be installed and several requirements for the environment will need to be prepared. First we will describe the required dependancies, after these are installed we can set up the appropriate environment to build, run, and test the DST.

### Dependancies
The DSD has a number of dependancies that are necessary both for building and deployment as well as for development. The primary development environment is currently Ubntu 22.04 but other environments will be added as requested. Currently, development of the Data Submission Tracker requires these software tools available or installed on the development system.

 - Docker
 - Google Cloud Platform (GCP)
   - GCP Account 
   - GCP Command Line Interface
 - Ansible

 See the [Install Prerequisites](#Install-Dependancies) section for how to install and set up each of these dependancies.

### Optional Dependancies
Because the Data Submission Tracker runs in a Docker container and all of the relevant code is run within the container these additional dependancies are not strictly necessary for installation on the development system. However, for testing and troubleshootin we recommend also installing the following dependancies.

 - Python v3.10.6 or higher
 - Django v4.1.4 - higher version not currently recommended

Installation of these Dependancies is fairly standard so we don't cover the details in this document.

### Provision PostgreSQL VM on GCP
The DST requires an external PostgreSQL accessed via HTML. This project uses an Ansible script to set up the project on an existing Google Cloud Platform Compute instance. We will first need to set up the GCP Compute Engine instance and then run the Ansible scripts to set up the PostgreSQL installation. This installation will then require some manual set up to allow for the Django database 

#### Create Compute Engine Instance
To create the GCP Compute Engine Instance navigate to the GCP site at `` and sign in. Select 'Compute Engine' -> 'VM instances' on the left-side menu. Select 'CREATE INSTANCE' button from the top menu bar to set up a new VM instance for the postgresql database. Settings for the new instance are as follows.

 | Setting | Value | Notes |
 | ------- | ------- | ------- |
 | Name |tracker-postgresql-tiny | You can use a different name |
 | Region | us-central1 (Iowa), us-central1-c | Choose a region near you |
 | Machhine Configuration | General Purpose |  |
 | Series | e2 |   |
 | Preset | e2-micro (2 vCPU, 1 GB memory) | Lowest cost configuration |
 | Boot Disk Image | Ubuntu 22.04 LTS (x86/64, amd64) | Current long-term-service Ubuntu |
 | On host maintenance | Migrate VM instance (Recommended) | e2 requires this |

Any setting not listed above should be left at the default setting.

#### Configure GCP Firewall
In order to access the Compute instance PostgreSQL database we will need to set up the firewall and networking tags for the VM instance. First set up a Firewall rule by selecting 'VPC networking' then 'Firewall' from the hamburger menu in the upper left corner of the page. On the Firewall page select 'CREATE FIREWALL RULE'. Use the following settings to create the new rule.

 | Setting | Value | Notes |
 | ------- | ------- | ------- |
 | Name | postgresql | You can choose a different name |
 | Description | Allow connection to the postgresql database on port 5432 |   |
 | Target tags | postgresql | You can use a different name, use this in the next section |
 | Source | IPv4 ranges | You may need to include IPv6 depending on your configuration |
 | Specified Protocols and Ranges | TCP | PostgreSQL communicates over TCP |
 | Ports | 5432 | This is the standard PostgreSQL port |

Any settings not listed above should be left at the default setting.

After setting up the firewall rule we need to add that rule to the Compute Engine Instance. Go back to 'Compute Engine' -> 'VM instances' and select our previously set up compute instance `tracker-posgresql-tiny`. Select 'Edit' and add `postgresql` to 'Network Tags'. The Compute Engine instance should now be ready for set-up as the postgresql data-source using Ansible playbooks from the repository.

#### Enable SSH on GCP VM
Use an existing SSH key or generate a new key with the following command.

``` shell
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub | xsel -b # Copy to clipboard
```

Next ssh in to the new VM either through the web interface or using the GCP CLI as below. Change zone, Compute Engine name and project to reflect the VM created above.

``` shell
gcloud compute ssh --zone "us-central1-c" "tracker-postgresql-tiny" --project "after-yesterday-392719"
sudo su ubuntu  # Change to user ubuntu
```

Once you have created the ssh connection and changed to the ubuntu user edit `~/.ssh/authorized_keys` and add the ssh key copied above. Now you should be able to log in locally with this key using the external IP addressed shown on the VM.

``` shell
ssh -i ~/.ssh/id_ed25519 ubuntu@<VM_EXTERNAL_IP>
```

Once you have verified you can ssh into the VM this setup is complete.

## Repository Setup
With the prerequisites installed and set up we are now ready to clone and setup the repository for development. Navigate to where you want the Git reepository located on your system and clone the repository with the following command.

``` shell
git clone git@github.com:amc-corey-cox/BDC_Dashboard.git
cd BDC_Dashboard
```

### Ansible Setup
Before completing the setup of the repository we need to setup and run the Ansible playbooks. In the `ansible` directory copy `inventory.example` to `inventory` and change the `ansible_host` ip address to the VM external IP address above. We also need to copy `group_vars/all/users.yml.example` to `group_vars/all/users.yml` and add the public key used for VM ssh above to authorized keys. The settings for `nimbus.yml` are already updated for dev in the repository. Finally in the `templates/` folder create a `.env` file with the following information.

``` .env
POSTGRES_DATA_DIR={{db_data_dir}}
POSTGRES_DB=tickets
POSTGRES_USER=postgres
POSTGRES_PASSWORD=
```

Ansible setup is now complete and you should be ready to run the Ansible playbooks. For further information on setting up Ansible it may be useful to read the documentation in `ansible/README.md`.

### Run Ansible Playbooks
These two Ansible playbooks set up the Ubuntu Compute Engine. First we will set up the Compute Engine for Docker.

``` shell
ansible-playbook -i inventory setup.yml
```

Then we will deploy the PostgreSQL Docker image and run it.

``` shell
ansible-playbook -i inventory deploy-pg.yml
```

### Finalize PostgreSQL Setup
One final manual setup step is necessary to complete the PostgreSQL setup for the database. We need to setup the initial password for the `postgres` (admin) user of the database. First log in to the VM with ssh using your external IP. 

``` shell
ssh -i ~/.ssh/id_ed25519 ubuntu@<VM_EXTERNAL_IP>
```

Once logged in change to super user and verify the docker image is running.

``` shell
sudo su
docker ps
```

Now we will run psql on the hosted Docker image to set the password for `postgres`.

``` shell
docker exec -it bdcat_database_1 psql -U postgres
```

In the `psql` shell change the password with this command.

``` sql
ALTER USER postgres WITH PASSWORD 'password';
```

Exit the psql shell and the ssh shell when you have finished setting the password. If you would like to check the PostgreSQL setup you can run psql (if installed) locally.

``` shell
psql -h <VM_EXTERNAL_IP> -U postgres -d tickets -p 5432
```

Now the PostgreSQL database should be ready to receive connections from the Django app. We will migrate the Django model automatically when we build the tracker container. However, if you have installed Django locally you can migrate the Django model manually see `ansible/README.md` for instructions.

### Environment Variables
For development purposes a number of environment variables need to be set. In the `api` folder create a `.env` file with the following data.

``` .env
# Environment variables
# For local development, the api directory should have an .env file with the following:

# Set to True for local dev and False for prod
DEBUG=True

# Set to DEBUG for local dev and INFO for prod
DJANGO_LOG_LEVEL=DEBUG

# The Project ID for GCP
GOOGLE_CLOUD_PROJECT=

# The SECRET_KEY generated by Django
SECRET_KEY=

# The Postgres database name
POSTGRES_DB=tickets

# The username of the Postgres User
POSTGRES_USER=postgres

# A (secure) password for the Postgres User
POSTGRES_PASSWORD=

# The external IP for the Compute Engine instance with Postgres
POSTGRES_HOST=

# The port for the Postgres Database
POSTGRES_PORT=5432

# The client ID for Google OAuth2
GOOGLE_CLIENT_ID=

# The client secret for Google OAuth2
GOOGLE_CLIENT_SECRET=


### Removing all SendGrid variables for now until we have a working dev environment.
# The API key for SendGrid
# SENDGRID_API_KEY=

# The admin group email
# SENDGRID_ADMIN_EMAIL=vanar@nhlbi.nih.gov

# The email address to use as the sender
# SENDGRID_NO_REPLY_EMAIL=no-reply@nhlbi.nih.gov

```

You will need to update `GOOGLE_CLOUD_PROJECT`, `SECRET_KEY`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `GOOGLE_CLIENT_ID`, and `GOOGLE_CLIENT_SECRET` with settings appropriate to your configuration from the steps in the [Prerequisites](#Prerequisites) section above. If you don't have a Django `SECRET_KEY` you can create one with the following command (Django local install required).

``` shell
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Build Tracker Docker Container
With the PostgreSQL database set up and running and the environment variables set, the repository should be ready for development. To test the development environment, we will build the Docker container and access the application.

First, build the Docker container using `docker-compose`.

``` shell
docker-compose up --build -d
```

To access the application navigate to `http://localhost:8000/` in your browser. You should see a login screen for the application with a button for `NIH login`. Login will not work at this time. In order to log in to the application we'll need to set the Django superuser. First, enter the local Docker container shell.

``` shell
docker exec -it bdc_dashboard_api_1 /bin/bash
```

Then create a Django superuser on the Docker container.

``` shell
python manage.py createsuperuser
```

Create a superuser with your desired credentials, generally your e-mail address and a password.

After creating the superuser you can authenticate on the Django app by navigating to `http://localhost:8000/admin`. Once authenticated, access the app at `http://localhost:8000/` to navigate the full application site. If all of these steps are successful you are now ready to begin development on the DMC Tracker app. 


---

# Install Dependancies

## Docker
Docker is an application containerization environment that allows software to be built in containers and deployed in different environments reducing dependancies and creating a more secure runtime environment by virtue of isolation from the host architecture. The Docker ecosystem provides both tools to create a container image and an engine to run those images on a target system. For basic build and development you will only need the container image creation tools. However for proper testing and to allow access to the software in a development environment we will install both the image creation and engine portions.

### Uninstall unofficial packages or conflicting dependancies
Some distributions have unofficial Docker packages installed or dependancies that Docker will install separately. We need to uninstall these to prevent conflicts.
```shell
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
I had a stub installation to satisfy another packages spurious dependancy. Here's how to check if a docker command still exists.
```shell
command -v docker
```
If the command still exists it is probably a stub. To check try running it. If there is no output, or a messagethat it isn't a real docker installation, check the file by opening it. If there is a stub file delete it. Replace '.local/bin/docker' with the path to your docker stub from the command above.
```shell
rm -rf .local/bin/docker
```

### System Requirements
Docker requires a 64-bit kernel (common on modern systems), 4 GB of RAM, configuring ID mapping in user namespaces enabled. The Docker Desktop also requires a systemd init, and a desktop environment. 

### Software Requirements
Docker requires KVM virtualization support and QEMU version 5.2 or newer, latest recommended.

#### KVM Support
First check KVM support by loading the module with the following command.
```shell
modprobe kvm
```
Then load the module specific to your systems processor.
```shell
modprobe kvm_intel  # Intel processors
modprobe kvm_amd    # AMD processors
```

If no errors are reported double check the modules are enabled.
```shell
lsmod | grep kvm
```
Output for this command should look similar to that below.
```shell
kvm_amd               167936  0
ccp                   126976  1 kvm_amd
kvm                  1089536  1 kvm_amd
irqbypass              16384  1 kvm
```
Next check ownership of the kvm device.
```shell
ls -al /dev/kvm
```
Add your user to the kvm group in order to access the kvm device.
```shell
sudo usermod -aG kvm $USER
```
You can check to make sure your user was added to the kvm group.
```shell
grep kvm /etc/group
```

#### Update QEMU to latest
Docker recommends updating QEMU to the latest version and requires at least version 5.2. Check your current version of QEMU.
```shell
/usr/bin/qemu-system-x86_64 --version
```
If this gives an error (mine did), you need to install QEMU.
```shell
sudo apt install qemu-system-x86
```
Unless you experience problems it is probably best to use the version of QEMU that is installed by your distribution. You can check the version.
```shell
kvm --version
```
For Ubuntu, the current version is 6.2. I'm currently using this for development and will update this file if I have any problems or decide to upgrade. The latest version as of this writing is 8.0.2.  
I have also installed some other recommended vertualization packages that may be useful or necessary for running and testing VMs locally.
```shell
sudo apt install qemu-kvm libvirt-clients libvirt-daemon-system bridge-utils virtinst libvirt-daemon
```
These may not be required and could even create conflicts but all of the information I found on installing QEMU suggested installing these as well. These sources also recommend enabling libvirtd.
```shell
sudo systemctl enable --now libvirtd
```
Sources also recommended installing virt-manager but I'll be using Docker Desktop to manage VMs so I'm skipping this for now.

## Install Docker
You can install the Docker packages from a package by downloading the package from the [Docker Linux Install](https://docs.docker.com/desktop/install/linux-install/) page. I prefer to manage my installation with apt. 

### Prepare for installation
Make sure everything is up-to-date and allow using a repository over HTTPS
```shell
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
```

### Add Docker GPG Key
We need the Docker official GPG public key to use their apt repository.
```shell
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

### Set up the Docker Apt Repository
This will set up the Docker Apt Repository allowing ongoing updates of Docker using the system software updater.
```shell
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Update Apt to fetch Docker Repository
We need to update the Apt cache in order to install from the Docker repository.
```shell
sudo apt-get update
```
This should show a line accessing downloader.docker.com for the systems installed release.

### Install Docker and tools
Now we can install Docker Engine, containerd, and Docker Compose. This will install the latest version, which is currently version 24.0.2.
```shell
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose docker-compose-plugin
```
If you need to install a different version see the [Docker Engine Installation](https://docs.docker.com/engine/install/ubuntu/#install-docker-engine)  

Now let's test the docker installation.
```shell
sudo docker run hello-world
```

### Fix Docker permissions
Docker requires root access to run. This is a security risk and we need to fix it. The recommended way to do this is to add your user to the docker group. This will allow your user to run docker commands without sudo.
```shell
sudo usermod -aG docker ${USER}
```
You will then need to login again or run the command below to gain the group permissions.
```shell
newgrp docker
```

### Install Docker Desktop
Docker Desktop is a GUI for managing Docker containers and VMs.
```shell
sudo apt install gnome-terminal
sudo apt remove docker-desktop
rm -r $HOME/.docker/desktop
sudo rm /usr/local/bin/com.docker.cli
sudo apt purge docker-desktop
```
Download the latest version of Docker Desktop from the [Docker Desktop](https://www.docker.com/products/docker-desktop) page. The latest version as of this writing is 4.1.1.

```shell
sudo apt-get update
sudo apt-get install ./docker-desktop-<version>-<arch>.deb
```

## Google Cloud Platform (GCP)
Setting up the PostgreSQL database with Ansible requires the Google Cloud Platform (GCP) including a GCP Compute Engine instance and local installation of the Command Line Interface (CLI).

### Google Cloud Platform Account
In order to You can sign into an existing account or create a new account at `https://cloud.google.com/`. Currently, new account sign-up gives $300 in credit

### GCP Compute Engine
To set up a GCP Compute Engine instance we will first need a GCP account.

### Google Cloud CLI
For Ubuntu/Debian Google Cloud CLI can be installed with the folowing instructions. If your system supports the signed-by option and your `apt-key` command supports the `--keyring` argument. If you are using a different distribution or your system doesn't support those commands see the instructions [here](https://cloud.google.com/sdk/docs/install#deb).
```
sudo apt-get update
sudo apt-get install apt-transport-https ca-certificates gnupg curl sudo
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install google-cloud-cli
```

After Google CLI is successfully installed initialize it with.
```
gcloud init
```

## Ansible
Ansible is an agentless automation tool that can manage multiple machines or devices remotely with SSH or other transports. The DSD uses Ansible to manage deployment and connectivity between separate elements of the DSD environment.

### Ansible Requirements
Ansible is a Python module which requires Python v2.9 or higher and is installed with pip. Check the system Python version.
```shell
python --version
```
And check to make sure pip is available.
```shell
python -m pip --version
```

### Install Ansible
Use pip to install Ansible system-wide.
```shell
python3 -m pip install --user ansible
```
Confirm Ansible is installed.
```shell
ansible --version
```
