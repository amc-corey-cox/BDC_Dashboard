# Red Hat OpenShift

> These manifest files can be used to deploy to a OpenShift cluster

## Prerequisites

- **[OpenShift CLI](https://docs.openshift.com/container-platform/4.7/cli_reference/openshift_cli/getting-started-cli.html)**

> NOTE: The rest of this README will assume you have experience with DevOps concepts and cluster administration

## CodeReady Containers

Currently, the changes are not tested on a live production cluster, but they work on a local OpenShift cluster.
You can view the console at: [`console-openshift-console.apps-crc.testing`](https://console-openshift-console.apps-crc.testing/)

## Pull Secret

Since the Quay repository is private, you must provide a secret to pull the images from the Quay repository.
In your Quay Robot Account, download the secret yml file

```
oc apply -f <secret.yml>
```

> NOTE: Replace `<secret.yml>` with the name of the file you downloaded

## Deployment

Deployment has been separated into files for each resource.

### [`deployment.yml`](./deployment.yml)

This contains the deployment configuration for the pod with the container running the app

```
oc apply -f deployment.yml
```

### [`service.yml`](./service.yml)

This contains the service configuration to redirect internal traffic to the pod

```
oc apply -f service.yml
```

### [`route.yml`](./route.yml)

This contains the route configuration to redirect web traffic to the pod

```
oc apply -f route.yml
```

### [`DeploymentConfig.yaml`](./DeploymentConfig.yaml)

This not tested, but follow the specs of the resouces above

> NOTE: This is a based off the templates written by Jason Wang

### [`BuildConfig.yaml`](./BuildConfig.yaml)

There is no need to build the image from source, it is already available in the Quay repository.
The [GitHub Actions Workflow](../.github/workflows/publish-to-quay.yml) is being used to deploy the image to the Quay repository.
This not tested, but _should_ work

> NOTE: This is a based off the templates written by Jason Wang
