[![](https://dcbadge.vercel.app/api/server/DWNCftGQZ3?theme=clean-inverted&logoColor=82C4FF)](https://discord.gg/DWNCftGQZ3)

# web3-copilot
Web3Copilot is an artificial intelligence tool developed using [Council by ChainML](https://github.com/chain-ml/council) to assist Web3 users navigate the ecosystem.

## Requirements
- Python >=3.9
- pip >=23.1

## Setup
- Create a new file called **.env**
    - Copy the contents of **.env.example** into your new **.env** file
    - API keys for third party tools are not provided.
        - `OPENAI_API_KEY` from [OpenAI](https://platform.openai.com/account/api-keys)
        - `OPENAI_LLM_MODEL` from [OpenAI Models](https://platform.openai.com/docs/models/continuous-model-upgrades)
        - `ETHERSCAN_API_KEY` from [Etherscan APIs](https://docs.etherscan.io/getting-started/viewing-api-usage-statistics)
        - `ETH_MAINNET_URL` from [Tenderly Dashboard > Web3 Gateway > Access Key](https://tenderly.co/web3-gateway)
        - `TENDERLY_API_KEY` from [Tenderly Dashboard > Account Settings > Authorization](https://docs.tenderly.co/simulations-and-forks/reference/configuration-of-api-access#get-an-api-key) 
- Create a virtual Python environment
  - `python -m venv ./venv`
- Activate the Python virtual env
  - Windows:
    - In cmd.exe: `venv\Scripts\activate.bat`
    - In PowerShell: `venv\Scripts\Activate.ps1`
  - Linux/MacOS: `source venv/bin/activate`
- Install the project dependencies:
  - `pip install -r requirements.txt`
- Generate PDF files:
  - `python web3_copilot/doc_retrieval/generate.py`

## Usage

### Run Agent Demo
- `python demo.py`

### Run Flask App

- `python app.py`
> _NOTE: this will run on port - http://127.0.0.1:8000_

## Cleanup
- Delete database
  - `rm -rf web3_copilot/doc_retrieval/data/database/chromadb`
- Deactivate virtual env
  - `deactivate`
- (optional) Delete virtual env
  - `rm -rf ./venv`

## Adding more docs from other web3 projects

> _NOTE: For the purpose of this tutorial, the script generates PDFs for projects that use Markdown files (.md) which are stored in the **docs/** folder in their documentation repository._

### Requirements
- Node >=12.22
- npm >= 6.14
- Git >=1.7

### Steps
- Update the `PROJECT_REPOS` dictionary in **web3_copilot/common/constants.py** as desired.
- Install [md-to-pdf](https://github.com/simonhaenisch/md-to-pdf)
  - `npm i -g md-to-pdf`
- Run `python web3_copilot/doc_retrieval/generate.py`

## Tutorial Jupyter Notebooks

### First Example
The **notebooks/** directory contains `first_example.ipynb`, an introductory notebook to Council.

To run this notebook:
- Go to the following [Google Colab](https://colab.research.google.com/drive/15DI-vIaaCPDFr6g49nxugHHqWuugtyRP?usp=sharing) link.
- If you would like to edit the notebook, you must first make a copy: Press File -> Save a Copy in Drive.

### Try out Council
The **notebooks/** directory also contains `council_getting_started.ipynb`, a Council tutorial for creating an Agent with _your own_ Skills and Chains.

To edit and run this notebook:
- Go to the following [Google Colab](https://colab.research.google.com/drive/1Tg_DCm92nCXEgslKdHwMc3-nj-Tpn6mO?usp=sharing) link.
- Press File -> Save a Copy in Drive.

### ETHToronto Tutorial

The **notebooks/** directory contains a file called `Web3Copilot_Tutorial.ipynb`, which has the missing code snippets for the tutorial.

To edit and run this notebook:
- Go to the following [Google Colab](...) link.
- Press File -> Save a Copy in Drive.


## ETHToronto Presentation
[Building AI Agents with ‘Council’](https://docs.google.com/presentation/d/1SHmsxBJOSp6tXP67Nv2LivcREJz2pkI6JU9VKnvxtKo/edit?usp=sharing).
