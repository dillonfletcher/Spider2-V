# coding=utf8
import json
import os, subprocess
from typing import Dict
from .general import get_vm_command_line
from .file import get_vm_file


def get_dbt_profiles(env, config: Dict[str, str]) -> str:
    """ Download dbt profiles.yml file from VM, search all possible paths and return the first one found.
    Paths include:
        config (Dict[str, Any]):
            dirs (List[str]): a list of possible dirs to search profiles.yml, if the path starts with a '$', it will be treated as an environment variable
            dest (str): local file name of the downloaded file
        working, default and environment variable DBT_PROFILES_DIR
    """
    for fp in config["dirs"]:
        if fp.startswith('$'):
            # fetching ENV vars does not work, because the command below is executed in a new shell in non-login, non-interactive mode
            # thus, the environment variable is not available
            fp = get_vm_command_line(env, {"command": ["/bin/bash", "-c", f"echo \"{fp}\""]})
            if type(fp) == str and fp.strip() != "":
                file = get_vm_file(env, {"path": fp.strip() + '/profiles.yml', "dest": config["dest"]})
                if file is not None:
                    return file
        else:
            file = get_vm_file(env, {"path": fp + '/profiles.yml', "dest": config["dest"]})
            if file is not None:
                return file

    return None


def get_dbt_project_info(env, config: Dict[str, str]):
    """ Retrieve the information on Dbt cloud projects.
    @args:
        env(desktop_env.envs.DesktopEnv): the environment object
        config (dict):
            setting_files: the path to the settings file, default is 'evaluation_examples/settings/dbt_cloud/settings.json'
            fields (list, required): the specific fields we want to extract for evaluation. Could be:
    """
    settings_file = config.get('settings_file', 'evaluation_examples/settings/dbt_cloud/settings.json')
    settings = json.load(open(settings_file, 'r'))

    os.environ["DBT_CLOUD_ACCOUNT_ID"] = settings["account_id"]
    os.environ["DBT_CLOUD_API_TOKEN"] = settings["token"]

    state = subprocess.run('dbt-cloud project list', shell=True, capture_output=True, text=True)
    project_list = json.loads(state.stdout)['data']

    if len(project_list) == 0:
        return "None"

    result = ""
    fields = config.get("fields", [])

    for field in fields:

        if field == "name":
            result += project_list[0]['name']
        elif field == "connection_type":
            connection = project_list[0]['connection']
            if connection is None:
                result += "None"
            else:
                result += connection['type']

        result += " "

    return result


def get_dbt_environment_info(env, config: Dict[str, str]):
    """ Retrieve the information on Dbt project environment. (Assume one project for each account)
    @args:
        env(desktop_env.envs.DesktopEnv): the environment object
        config (dict):
            setting_files: the path to the settings file, default is 'evaluation_examples/settings/dbt_cloud/settings.json'
            name (required): the name of to-be-evaluate environment
            fields (list, required): the specific fields we want to extract for evaluation. Could be:
    """
    settings_file = config.get('settings_file', 'evaluation_examples/settings/dbt_cloud/settings.json')
    settings = json.load(open(settings_file, 'r'))

    os.environ["DBT_CLOUD_ACCOUNT_ID"] = settings["account_id"]
    os.environ["DBT_CLOUD_API_TOKEN"] = settings["token"]

    state = subprocess.run('dbt-cloud project list', shell=True, capture_output=True, text=True)
    project_list = json.loads(state.stdout)['data']

    if len(project_list) == 0:
        return "None"

    os.environ["DBT_CLOUD_PROJECT_ID"] = str(project_list[0]['id'])

    state = subprocess.run('dbt-cloud environment list', shell=True, capture_output=True, text=True)
    env_list = json.loads(state.stdout)['data']

    result = ""
    name = config.get("name", "New Environment")
    fields = config.get("fields", [])

    found = False
    for env in env_list:
        if env['name'] == name:
            found = True
            for field in fields:
                result += env[field]
                result += " "

    if not found:
        return "None"
    return result
