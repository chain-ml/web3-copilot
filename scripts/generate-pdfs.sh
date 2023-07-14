#!/usr/bin/env bash

project_repos=(
    "uniswap::https://github.com/Uniswap/docs.git"
    "avalanche::https://github.com/ava-labs/avalanche-docs.git"
    "cosmos::https://github.com/cosmos/cosmos-sdk.git"
    "polygon::https://github.com/maticnetwork/matic-docs.git"
)

source_docs_dir="../source-docs"
data_dir="../data"

project_docs_folder="docs"

for index in "${project_repos[@]}" ; do
    project_name="${index%%::*}"
    repo_url="${index##*::}"

    project_repo_dir="${source_docs_dir}/$project_name"
    mkdir "${project_repo_dir}"

    echo "Cloning docs for $project_name: $repo_url"
    if [ ! -d  "${project_repo_dir}/.git" ]; then
      git clone $repo_url "${project_repo_dir}"
    else
      cd "${project_repo_dir}"
      git pull $repo_url
      cd ..
    fi
    echo "Cloned docs for $project_name($repo_url) to $project_repo_dir"

    project_data_dir="${data_dir}/$project_name"
    echo "Creating data dir${project_data_dir}"
    mkdir "${project_data_dir}"

    echo "Generating PDF for $project_name"

    find "${project_repo_dir}/$project_docs_folder" -type f -name "*.md" -exec cat {} \; | md-to-pdf > "${project_data_dir}/$project_name-docs.pdf"

    echo "Generated PDF for $project_name"

done

