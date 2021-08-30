import os
import warnings
from typing import Union
import numpy as np
import pandas as pd
from utils import *


def check_results_dict_dimensions(result_dict: dict):
    """
    Check that all keys in results dictionary have the same dimension.
    :param result_dict: Results of dictionary.
    :return: Nothing.
    """
    check_list = []
    error_message = []
    for key, value in result_dict.items():
        error_message.append(f'{key}: {", ".join([str(item) for item in value])}\n')
        check_list.append(len(value))
    if len(set(check_list)) > 1:
        raise ValueError(f'Result dictionary has unbalanced values: {"; ".join(error_message)}')


def get_single_response_value(dom_response_list: list):
    """
    Get value of a single scenario's response.
    :param dom_response_list: Single response provided as a list of one term.
    :return: Value of such observation.
    """
    response_list = extract_list_from_dom(dom_object=dom_response_list[0],
                                          tag_name='Observation',
                                          attribute_name='Value')
    if len(response_list) == 0:
        response_value = np.NaN
    else:
        response_value = response_list[0]
    return response_value


def load_scenario_results(result_dict: dict,
                          dom_scenario_list: minidom.Document,
                          response_list: set,
                          scenario_name: str):
    """
    Load scenario response and value to result_dict. Scenario name is set outside this function.
    :param scenario_name:
    :param result_dict: Dictionary of results to be updated.
    :param dom_scenario_list: List of.
    :param response_list: Set of response names to iterate over.
    :return: Nothing. Result dictionary is updated
    """
    for resp in response_list:
        response = filter_dom_by_attribute(list_of_doms=dom_scenario_list,
                                           attribute_name='Response',
                                           attribute_value=resp)
        value_response = get_single_response_value(dom_response_list=response)
        result_dict['scenario'].append(scenario_name)
        result_dict['response'].append(resp)
        result_dict['value'].append(value_response)


def load_single_experiment_result(experiment_path: str) -> Union[pd.DataFrame, None]:
    """
    Load results of single experiment
    :param experiment_path:
    :return: DataFrame with result of experiment.
    """
    try:
        project_xml = minidom.parse(experiment_path)
    except FileNotFoundError:
        warnings.warn(f'Experiment {experiment_path} has not been ran yet.')
        return None
    scenarios_names = set(extract_list_from_dom(dom_object=project_xml,
                                                tag_name='Observations',
                                                attribute_name='Scenario'))
    response_names = set(extract_list_from_dom(dom_object=project_xml,
                                               tag_name='Observations',
                                               attribute_name='Response'))
    results_dict = {'scenario': list(), 'response': list(), 'value': list()}
    for sce in scenarios_names:
        scenario_list = filter_dom_by_attribute(list_of_doms=extract_list_from_dom(dom_object=project_xml,
                                                                                   tag_name='Observations'),
                                                attribute_name='Scenario',
                                                attribute_value=sce)
        load_scenario_results(result_dict=results_dict,
                              dom_scenario_list=scenario_list,
                              response_list=response_names,
                              scenario_name=sce)
        check_results_dict_dimensions(results_dict)
    results_df = pd.DataFrame(results_dict)
    results_df = results_df.pivot(index='scenario', columns='response', values='value')
    return results_df


def load_experiment_results(project_path: str,
                            project_filename: str,
                            model_name: str) -> dict:
    """
    Load all experiment results related to a Simio model.
    :param project_path:
    :param project_filename:
    :param model_name:
    :return: Dictionary whose keys are experiment name and value is a data frame (or None).
    """
    file_path = os.path.join(project_path, project_filename)
    experiment_list = get_experiment_names(path=file_path, model_name=model_name)
    folder_name = get_project_folder_name(project_file_name=project_filename)
    experiment_dictionary = {'experiment_name': [], 'results': []}
    for exp_name in experiment_list:
        experiments_path = os.path.join(project_path, folder_name, 'Results', model_name, exp_name)
        experiment_dictionary['experiment_name'].append(exp_name)
        experiment_dictionary['results'].append(load_single_experiment_result(experiments_path))
    return experiment_dictionary


def get_experiment_names(path: str,
                         model_name: str):
    """
    List of experiment names.
    :param path: path to Simio project.
    :param model_name: Name of the file.
    :return: List of experiment names.
    """
    project_xml = minidom.parse(path)
    list_of_models = extract_list_from_dom(dom_object=project_xml, tag_name='Model')
    model = get_model_from_list_of_doms(list_of_doms=list_of_models, model_name=model_name)
    experiment_list = extract_list_from_dom(dom_object=model,
                                            tag_name='Experiment',
                                            attribute_name='Name',
                                            suffix_str=' ResponseResults.xml')
    return experiment_list


if __name__ == '__main__':
    env_project_path = os.environ['SIMIOPROJECTPATH']
    env_project_file = os.environ['SIMIOPROJECTNAME']
    env_model_name = os.environ['MODELNAME']
    load_experiment_results(project_path=env_project_path,
                            project_filename=env_project_file,
                            model_name=env_model_name)
