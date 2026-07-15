# WorkFlow Pro Automation Testing Engine

This repository holds the automated quality assurance E2E engine for WorkFlow Pro, supporting multi-tenant isolation verification, cross-browser web testing, and BrowserStack mobile executions.

## Prerequisites
* Python 3.10 or higher installed.
* Node.js (for Playwright system dependency matching).

##  Installation & System Configuration

1. Clone this repository to your environment directory:

git clone [https://github.com/workflowpro/automation-framework.git](https://github.com/workflowpro/automation-framework.git)
cd automation-framework


2.Establish an isolated virtual environment and activate it:

python -bin/vcvarsall.bat or python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

3.Install the application dependencies:

pip install -r requirements.txt

4.Install the required Playwright headless engine binaries:

playwright install --with-deps

5.Populate your configuration fields inside a local execution properties file:

cp .env.example .env
# Edit the created .env file to supply your system keys and API tokens.



# Running Tests
1.Run the complete suite locally in headless mode:

pytest

2.Execute tests targeting a specific browser engine context:

pytest --browser=webkit

3.Run tests in parallel across multiple CPU cores:

pytest -n auto