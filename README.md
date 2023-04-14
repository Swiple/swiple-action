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
name: Dataset Validation

on: [pull_request]

jobs:
  dataset_validation:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Swiple Dataset Validation
      uses: your_github_username/swiple-action@v1
      with:
        api_base_url: ${{ secrets.API_BASE_URL }}
        client_id: ${{ secrets.CLIENT_ID }}
        client_secret: ${{ secrets.CLIENT_SECRET }}
        username: ${{ secrets.USERNAME }}
        password: ${{ secrets.PASSWORD }}
        dataset_id: 'your_dataset_id'
```
