# Introduction
This guide will provide instruction and information on setting up the development environment for the BioData Catalyst (BDC) Data Management Core (DMC) Data Submission Dashboard (DSD). This will include installing prerequisites, setting up a development environment, building the container, deploying to BioData Catalyst, running tests/linting, and information about contributing to development.

# Prerequisites
The DSD has a number of dependancies that are necessary both for building and deployment as well as for development. This section will describe how to install and set up each of these dependancies. The primary development environment is currently Ubntu 22.04 but other environments will be added as requested.

## Ansible
Ansible is an agentless automation tool that can manage multiple machines or devices remotely with SSH or other transports. The DSD uses Ansible to manage deployment and connectivity between separate elements of the DSD environment.

## Docker
Docker is an application containerization environment that allows software to be built in containers and deployed in different environments reducing dependancies and creating a more secure runtime environment by virtue of isolation from the host architecture. The Docker ecosystem provides both tools to create a container image and an engine to run those images on a target system. For basic build and development you will only need the container image creation tools. However for proper testing and to allow access to the software in a development environment we will install both the image creation and engine portions.

### Uninstall unofficial packages or conflicting dependancies
Some distributions have unofficial Docker packages installed or dependancies that Docker will install separately. We need to uninstall these to prevent conflicts.
```
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
I had a stub installation to satisfy another packages spurious dependancy. Here's how to check if a docker command still exists.
```
command -v docker
```
If the command still exists it is probably a stub. To check try running it. If there is no output, or a messagethat it isn't a real docker installation, check the file by opening it. If there is a stub file delete it. Replace '.local/bin/docker' with the path to your docker stub from the command above.
```
rm -rf .local/bin/docker
```

### System Requirements
Docker requires a 64-bit kernel (common on modern systems), 4 GB of RAM, configuring ID mapping in user namespaces enabled. The Docker Desktop also requires a systemd init, and a desktop environment. 

### Software Requirements
Docker requires KVM virtualization support and QEMU version 5.2 or newer, latest recommended.

#### KVM Support
First check KVM support by loading the module with the following command.
```
modprobe kvm
```
Then load the module specific to your systems processor.
```
modprobe kvm_intel  # Intel processors
modprobe kvm_amd    # AMD processors
```

If no errors are reported double check the modules are enabled.
```
lsmod | grep kvm
```
Output for this command should look similar to that below.
```
kvm_amd               167936  0
ccp                   126976  1 kvm_amd
kvm                  1089536  1 kvm_amd
irqbypass              16384  1 kvm
```
Next check ownership of the kvm device.
```
ls -al /dev/kvm
```
Add your user to the kvm group in order to access the kvm device.
```
sudo usermod -aG kvm $USER
```
You can check to make sure your user was added to the kvm group.
```
grep kvm /etc/group
```

#### Update QEMU to latest
Docker recommends updating QEMU to the latest version and requires at least version 5.2. Check your current version of QEMU.
```
/usr/bin/qemu-system-x86_64 --version
```
If this gives an error (mine did), you need to install QEMU.
```
sudo apt install qemu-system-x86
```
Unless you experience problems it is probably best to use the version of QEMU that is installed by your distribution. You can check the version.
```
kvm --version
```
For Ubuntu, the current version is 6.2. I'm currently using this for development and will update this file if I have any problems or decide to upgrade. The latest version as of this writing is 8.0.2.  
I have also installed some other recommended vertualization packages that may be useful or necessary for running and testing VMs locally.
```
sudo apt install qemu-kvm libvirt-clients libvirt-daemon-system bridge-utils virtinst libvirt-daemon
```
These may not be required and could even create conflicts but all of the information I found on installing QEMU suggested installing these as well. These sources also recommend enabling libvirtd.
```
sudo systemctl enable --now libvirtd
```
Sources also recommended installing virt-manager but I'll be using Docker Desktop to manage VMs so I'm skipping this for now.

## Install Docker
You can install the Docker packages from a package by downloading the package from the [Docker Linux Install](https://docs.docker.com/desktop/install/linux-install/) page. I prefer to manage my installation with apt. 

### Prepare for installation
Make sure everything is up-to-date and allow using a repository over HTTPS
```
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
```

### Add Docker GPG Key
We need the Docker official GPG public key to use their apt repository.
```
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

### Set up the Docker Apt Repository
This will set up the Docker Apt Repository allowing ongoing updates of Docker using the system software updater.
```
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Update Apt to fetch Docker Repository
We need to update the Apt cache in order to install from the Docker repository.
```
sudo apt-get update
```
This should show a line accessing downloader.docker.com for the systems installed release.

### Install Docker and tools
Now we can install Docker Engine, containerd, and Docker Compose. This will install the latest version, which is currently version 24.0.2.
```
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
If you need to install a different version see the [Docker Engine Installation](https://docs.docker.com/engine/install/ubuntu/#install-docker-engine)  

Now let's test the docker installation.
```
sudo docker run hello-world
```

##
