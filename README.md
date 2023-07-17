# web3-copilot
Web3Copilot is artificial intelligence tool developed using [CouncilAI by ChainML](https://github.com/chain-ml/council) to assist Web3 users navigate the ecosystem.

## Requirements
- Python >=3.9
- pip >=23.1

## Setup
- Create a new file called **.env**
    - Copy the contents of **.env.example** into your new **.env** file
    - API keys for third party tools are not provided.
        - `OPENAI_API_KEY` from [OpenAI](https://platform.openai.com/account/api-keys)
        - `OPENAI_LLM_MODEL` from [OpenAI Models](https://platform.openai.com/docs/models/continuous-model-upgrades)
- Create a virtual Python environment
  - `python -m venv ./venv`
- Activate the Python virtual env
  - Windows:
    - In cmd.exe: `venv\Scripts\activate.bat`
    - In PowerShell: `venv\Scripts\Activate.ps1`
  - Linux/MacOS: `source venv/bin/activate`
- Install the project dependencies:
  - `pip install -r requirements.txt`
- Generate PDF files with either option
  - Python:
    - `python generate.py`
  - Bash:
    - `cd scripts`
    - `sh generate-pdfs.sh`

## Usage

### Run Agent Demo
- `python demo.py`

### Run Flask App

#### Within a virtual environment
- `flask run`
  - If you'd like to run it in debug mode, append the `--debug` flag to the above command
> Note that this will run on the default Flask port 5000 - http://127.0.0.1:5000

#### From a terminal
- `python demo.py`
> Note that this will run on port - http://127.0.0.1:8000

## Cleanup
- Delete database
  - `rm -rf database/chromadb`
- Deactivate virtual env
  - `deactivate`
- (optional) Delete virtual env
  - `rm -rf ./venv`

## Adding more docs from web3 projects

> NOTE: For the purpose of this tutorial, the script generates PDFs for projects that use Markdown files (.md) which are stored in the **docs/** folder in their documentation repository.

### Requirements
- Node >=12.22
- npm >= 6.14
- Git >=1.7

### Steps
- Update the `project_repos` dictionary in **generate.py** as desired
- Install [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf)
  - `npm i -g md-to-pdf`
- Run `python generate.py`
  - alternatively with bash:
    - `cd scripts`
    - `sh generate-pdfs.sh`
