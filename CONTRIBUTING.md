# Introduction
This guide will provide instruction and information on setting up the development environment for the BioData Catalyst (BDC) Data Management Core (DMC) Data Submission Tracker (DST). This will include installing prerequisites, setting up a development environment, building the container, deploying to BioData Catalyst, running tests/linting, and information about contributing to development.
> At this point all installation is managed system-wide. I think this is a poor way to manage a development environment. I would prefer that we use an environmental encapsulation of some sort, such as poetry or pyenv. We will try to move towards some encapsulation after we have an initial working environment.

# Prerequisites
In order to build and run the Data Submisison tracker several dependancies will need to be installed and several requirements for the environment will need to be prepared. First we will describe the required dependancies, after these are installed we can set up the appropriate environment to build, run, and test the DST.

## Dependancies
The DSD has a number of dependancies that are necessary both for building and deployment as well as for development. The primary development environment is currently Ubntu 22.04 but other environments will be added as requested. Currently, development of the Data Submission Tracker requires these software tools available or installed on the development system.

 - Docker
 - Google Cloud Platform (GCP)
   - GCP Account 
   - GCP Command Line Interface
 - Ansible

 See the [Install Prerequisites](#Install-Dependancies) section for how to install and set up each of these dependancies.

## Optional Dependancies
Because the Data Submission Tracker runs in a Docker container and all of the relevant code is run within the container these additional dependancies are not strictly necessary for installation on the development system. However, for testing and troubleshootin we recommend also installing the following dependancies.

 - Python v3.10.6 or higher
 - Django v4.1.4 - higher version not currently recommended

Installation of these Dependancies is fairly standard so we don't cover the details in this document.

## Provision PostgreSQL VM on GCP
The DST requires an external PostgreSQL accessed via HTML. This project uses an Ansible script to set up the project on an existing Google Cloud Platform Compute instance. We will first need to set up the GCP Compute Engine instance and then run the Ansible scripts to set up the PostgreSQL installation. This installation will then require some manual set up to allow for the Django database 

### Create Compute Engine Instance
To create the GCP Compute Engine Instance navigate to the GCP site at `` and sign in. Select 'Compute Engine' -> 'VM instances' on the left-side menu. Select 'CREATE INSTANCE' button from the top menu bar to set up a new VM instance for the postgresql database. Settings for the new instance are as follows.

 | Setting | Value | Notes |
 | ------- | ------- | ------- |
 | Name |tracker-postgresql-tiny | You can use a different name |
 | Region | us-central1 (Iowa), us-central1-c | Choose a region near you |
 | Machhine Configuration | General Purpose |  |
 | Series | e2 |   |
 | Preset | e2-micro (2 vCPU, 1 GB memory) | Lowest cost configuration |
 | Boot Disk Image | Ubuntu 22.04 LTS (x86/64, amd64) | Current long-term-service Ubuntu |
 | Firewall | postgresql | We need to be able to reach the VM |
 | On host maintenance | Migrate VM instance (Recommended) | e2 requires this |

Any setting not listed above should be left at the default setting.

### Configure Firewall
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


## Environment Variables



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

# Set up Development Environment
For development, the `api` directory should have a `.env` containing environment variables.
The values of these variables will be different for the production environment.

# 

