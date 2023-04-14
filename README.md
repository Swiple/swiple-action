# Swiple Dataset Validation Action

This GitHub action automatically validates datasets, polls task status, and displays validation results in a GitHub pull request. It is designed to work with Swiple's dataset validation API.

## Features

- Authenticate with the Swiple API using provided credentials
- Run dataset validation and obtain a task ID
- Poll the task status until it reaches a final state (SUCCESS, FAILURE, or ERROR)
- Retrieve the most recent validation results for a specific dataset ID
- Display validation results as a table in the GitHub pull request

## Usage

To use this action, you need to add it as a step in your GitHub Actions workflow file (`.github/workflows/main.yml` or similar). Here's an example workflow:

```yaml
name: Swiple Dataset Validation

on: [pull_request]

jobs:
  validate-dataset:
    runs-on: ubuntu-latest

    steps:
    - name: Check out repository
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: 3.9
        
    - name: Validate Dataset
      uses: Swiple/swiple-action@v1
      with:
        api_base_url: 'https://swiple.api.yourdomain.io'
        ui_base_url: 'https://swiple.app.yourdomain.io'
        dataset_id: 'your_dataset_id'
        username: ${{ secrets.API_USERNAME }}
        password: ${{ secrets.API_PASSWORD }}
        github_token: ${{ secrets.GITHUB_TOKEN }}
        require_all_passed: 'true'  # OPTIONAL: Causes build to fail if any expectations fail
```
