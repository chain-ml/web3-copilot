import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath('../web3-copilot'))

from web3_copilot.common import constants

PROJECT_REPO_DOCS_PATH = "docs"

for project in constants.PROJECT_REPOS:
    repo_url = constants.PROJECT_REPOS[project]

    print(f"Cloning docs for {project}: {repo_url}")

    project_repo_dir = os.path.join(constants.SOURCE_DOCS, project)
    if not os.path.exists(project_repo_dir):
        subprocess.run(f"mkdir {project_repo_dir}", shell=True)
        subprocess.run(
            f'git clone {repo_url} {project_repo_dir}',
            shell=True
        )

    print(f"Cloned {project}({repo_url}) to {project_repo_dir}")

    project_data_dir = os.path.join(constants.DATA_DIR, project)
    print(f"Creating data dir: {project_data_dir}")
    if not os.path.exists(project_data_dir):
        os.mkdir(project_data_dir)

    print(f"Generating PDF for {project}")

    subprocess.run(
        f'find "{project_repo_dir}/{PROJECT_REPO_DOCS_PATH}" -type f -name "*.md" -exec cat {{}} \; \
        | md-to-pdf > "{project_data_dir}/{project}-docs.pdf"',
        shell=True
    )

    print(f"Generated PDF for {project}")
