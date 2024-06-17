# NHLBI BioData Catalyst | Data Management Core | Data Submission Tool
> A web-based tool for following the progress of Data Submissions through the NHLBI BioData Catalyst Data Management Core ingest pipeline, allowing self-service data submission and tracking.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

The NHLBI BioData Catalyst Data Management Core (DMC) Data Submission Tool (DST) is a web-based tool that aids users in submitting data to NHLBI BioData Catalyst with the Data Management Core. The tool provides a user-friendly interface for tracking the progress of data submissions through the ingest pipeline. The tool will also provide self-service data submission capabilities, such as allowing users to create a new submission or ask questions about an existing submission without requiring additional resources.

The Data Management Core pipeline documentation can be found in the [Instructions for Data Submission to BDC](https://bdcatalyst.gitbook.io/biodata-catalyst-documentation/data-management/data-submission-instructions).

The Data Submission Tool is a Django web application calling Jira and Freshdesk API's to track the progress of data submissions and provide self-service data submission capabilities. The tool is designed to be deployed on a cloud platform, such as Google Cloud Platform (GCP) or Amazon Web Services (AWS), and is built using the Django web framework in Docker containers with a PostgreSQL database.

# Development Documentation
The development is planned to proceed based on the requirements and design documents listed below.

Link for current DMC Data Submission Dashboard requirements document (access on request):
https://docs.google.com/document/d/1cInDpmWSq92_OVRo6zFKwEFiCIzZ3pY-cNB_9pmhrdM/edit?usp=sharing

Link for DMC Data Submission Dashboard diagrams in draw.io (access on request):
https://drive.google.com/file/d/1IEgmn_Q8E52BPPpQqsEPRSHZ0BrKtxCa/view?usp=sharing

Link for the DMC Data Submission Tool - Self-Service Data Submission Component (access on request):
https://docs.google.com/document/d/1MYZlWF_bd4-KEuh0SVkA0MqjwwFL0GP1/view?usp=sharing

## For Developers
See the CONTRIBUTING.md file for information on how to set up the repository for development and install the prerequisites.

