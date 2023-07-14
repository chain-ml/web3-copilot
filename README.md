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

## Usage
- `python agent.py`

## Cleanup
- Delete database
  - `rm -rf database/chromadb`
- Deactivate virtual env
  - `deactivate`
- (optional) Delete virtual env
  - `rm -rf ./venv`

## Adding more docs from web3 projects

### Requirements
- Node >=12.22
- npm >= 6.14

### Setup
- Create a new folder in **source-docs/** for the web3 project of your choice:
  - `mkdir avalanche`
- Clone the project's docs repo into this new folder:
  - `cd avalanche`
  - `git clone git@github.com:ava-labs/avalanche-docs.git`
- Install [md-to-pdf](https://www.npmjs.com/package/md-to-pdf) with npm:
  - `npm i -g md-to-pdf`
- Convert all **.md** files in the appropriate dir (**avalanche-docs/docs/** in this case) using _md-to-pdf_:
  - `cat avalanche-docs/docs/**/*.md | md-to-pdf > avalanche-docs.pdf`
- Create a new folder in **data/**:
  - `mkdir ../data/avax`
- Copy/move the newly generated PDF file to the data directory:
  - ` cp avalanche-docs.pdf ../data/avax`
      
  