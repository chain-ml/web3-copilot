import constants
import os
import subprocess

from git import Repo

project_repos = {
    "uniswap": "https://github.com/Uniswap/docs.git",
    "avalanche": "https://github.com/ava-labs/avalanche-docs.git",
    "cosmos": "https://github.com/cosmos/cosmos-sdk.git",
    "polygon": "https://github.com/0xPolygon/wiki.git"
}

DOCS_FOLDER = "docs"

for project in project_repos:
    repo_url = project_repos[project]

    print(f"Cloning docs for {project}: {repo_url}")

    project_repo_dir = os.path.join(constants.SOURCE_DOCS, project)
    if not os.path.exists(project_repo_dir):
        Repo().clone_from(repo_url, project_repo_dir)

    print(f"Cloned {project}({repo_url}) to {project_repo_dir}")

    project_data_dir = os.path.join(constants.DATA_DIR, project)
    print(f"Creating data dir: {project_data_dir}")
    if not os.path.exists(project_data_dir):
        os.mkdir(project_data_dir)

    print(f"Generating PDF for {project}")

    subprocess.run(
        f'find "{project_repo_dir}/{DOCS_FOLDER}" -type f -name "*.md" -exec cat {{}} \; \
        | md-to-pdf > "{project_data_dir}/{project}-docs.pdf"',
        shell=True
    )

    print(f"Generated PDF for {project}")
