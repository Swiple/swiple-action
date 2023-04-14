import os
import time
import requests

from datetime import datetime
from github import Github
from zoneinfo import ZoneInfo


api_base_url = os.environ['API_BASE_URL']
username = os.environ['USERNAME']
password = os.environ['PASSWORD']
dataset_id = os.environ['DATASET_ID']
time_zone = os.environ.get("TIME_ZONE", "US/Central")
github_token = os.environ['GITHUB_TOKEN']

session = requests.Session()


def authenticate():
    url = f"{api_base_url}/auth/login"
    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
    }
    response = session.post(url, data=data)
    response.raise_for_status()


def get_dataset(key):
    url = f"{api_base_url}/datasets/{key}"
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def validate_dataset(key):
    url = f"{api_base_url}/datasets/{key}/validate"
    response = session.post(url)
    response.raise_for_status()
    return response.json()['task_id']


def get_task(task_id):
    url = f"{api_base_url}/tasks/{task_id}"
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def poll_task_status(task_id):
    while True:
        task = get_task(task_id)
        status = task['status']
        if status == 'SUCCESS':
            return task
        elif status in ('FAILURE', 'ERROR'):
            raise Exception(f"Task failed with status {status}: {task['result']}")
        else:
            time.sleep(5)


def get_validations(dataset_id):
    url = f"{api_base_url}/expectations?dataset_id={dataset_id}&include_history=true&enabled=true&asc=false"
    response = session.get(url)
    response.raise_for_status()
    return response.json()


def process_validation_result(result: dict, result_type: str):
    if result_type == "column_map_expectation":
        result_value = f'{round(100 - result["result"]["unexpected_percent"], 5)}%'
    elif result_type == "column_aggregate_expectation":
        result_value = round(result["result"]["observed_value"], 5)
    elif result_type == "expectation":
        if "observed_value" in result["result"]:
            result_value = round(result["result"]["observed_value"], 5)
        elif "observed_value_list" in result["result"]:
            result_value = '-'
        else:
            raise ValueError(f"{result_type} not implemented. Data")
    else:
        raise ValueError(f"{result_type} not implemented. Data")

    return result_value


def format_run_time(date_string: str):
    dt = datetime.fromisoformat(date_string.replace("Z", "+00:00"))

    # Convert the datetime object to US Central Time
    desired_timezone = ZoneInfo(time_zone)
    localized_dt = dt.astimezone(desired_timezone)

    # Format the datetime object for easy viewing
    formatted_date = localized_dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
    return formatted_date


def post_pr_comment(repo_name, pr_number, message):
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_issue_comment(message)


def main():
    authenticate()
    dataset = get_dataset(dataset_id)
    task_id = validate_dataset(dataset_id)
    task = poll_task_status(task_id)
    validations = get_validations(dataset_id)

    validation_results = []
    passed_expectations_count = 0

    for expectation in validations:
        if expectation.get("validations")[0]['exception_info']['exception_message']:
            status = '❗'
        else:
            if expectation.get("validations")[0]['success']:
                status = '✅'
                passed_expectations_count += 1
            else:
                status = '❌'

        result = {
            "expectation_type": expectation.get("expectation_type"),
            "success": status,
            "result_value": process_validation_result(expectation.get("validations")[0], expectation["result_type"]),
            "documentation": expectation.get("documentation"),
            "column": expectation.get('kwargs', {}).get("column", ''),
            "kwargs": expectation.get("kwargs"),
        }
        validation_results.append(result)

    total_expectations_count = len(validations)

    # Format the validation results as a table
    table_header = "| Column | Expectation | Success | Result | Documentation |\n| --- | --- | --- | --- | --- |\n"
    table_rows = [
        f"| {result['column']} | {result['expectation_type']} | {result['success']} | {result['result_value']} | {result['documentation']} |"
        for result in validation_results
    ]

    status_icon = "✅" if total_expectations_count == passed_expectations_count else "❌"
    table = f"<details>\n<summary>Validation Results — {status_icon} {passed_expectations_count} of {total_expectations_count} expectations passed</summary>\n<br/>\n{table_header}" + "\n".join(
        table_rows) + "\n</details>"

    engine = dataset["engine"]
    datasource_name = dataset["datasource_name"]
    database = dataset["database"]
    dataset_name = dataset["dataset_name"]
    run_time = format_run_time(validations[0].get("validations")[0]["run_time"])

    overview_header = "| Engine | Datasource Name | Database | Dataset Name | Run Time |\n|---|---|---|---|---|\n"
    overview_table_row = f"|{engine}|{datasource_name}|{database}|{dataset_name}|{run_time}|"
    overview_table = overview_header + overview_table_row

    markdown = f"{overview_table}\n\n{table}"

    # Post the validation results as a PR comment
    repo_name = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["INPUT_PR_NUMBER"])

    post_pr_comment(repo_name, pr_number, markdown)


if __name__ == "__main__":
    main()
