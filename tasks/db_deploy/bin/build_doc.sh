#!/bin/bash
## =============================================================================
## NAME: build_doc.sh
##
##
## DESCRIPTION
## -----------------------------------------------------------------------------
## Builds the lambda (task) API documentation.
##
##
## USAGE
## -----------------------------------------------------------------------------
## bin/build_doc.sh
##
## This must be called from the (root) lambda directory /tasks/db_deploy
## =============================================================================

## Set this for Debugging only
#set -ex

## Make sure we are calling the script the correct way.
BASEDIR=$(dirname $0)
if [ "$BASEDIR" != "bin" ]; then
  >&2 echo "ERROR: This script must be called from the root directory of the task lambda [bin/build.sh]."
  exit 1
fi


source ../../bin/common/check_returncode.sh


## MAIN
## -----------------------------------------------------------------------------
## Create the virtual env. Remove it if it already exists.
echo "INFO: Creating virtual environment ..."
if [ -d venv ]; then
  rm -rf venv
  find . -type d -name "__pycache__" -exec rm -rf {} +
fi

python3 -m venv venv
source venv/bin/activate
trap 'deactivate' EXIT

## Install the requirements
pip install -q --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org
pip install -q pydoc-markdown==3.10.1 --trusted-host pypi.org --trusted-host files.pythonhosted.org
check_returncode $? "ERROR: pip install encountered an error."

## Get the modules we want to document
file_list=$(find . \
    -type d \
    \( -path ./test -o -path ./venv -o -path ./.vscode \) -prune \
    -o -type f \
    -name "*.py" \
    -print \
    | sed 's|^./||' \
    | sort)
module_list=""
first_time="1"
for file in $file_list
do
    module=${file%%".py"}
    if [ "${first_time}" = "1" ]; then
        module_list="-m ${module}"
        first_time="0"
    else
        module_list="${module_list} -m ${module}"
    fi
done

echo "INFO: Creating API markdown file ..."
## Run the documentation command
echo "INFO: Creating API documentation ..."
pydoc-markdown -I . ${module_list} --render-toc > API.md
check_returncode $? "ERROR: Failed to create API.md file."

## Perform cleanup
echo "INFO: Cleaning up environment ..."
rm -rf venv
find . -type d -name "__pycache__" -exec rm -rf {} +

exit 0
