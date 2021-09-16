import datetime
import warnings
from xml.dom import minidom
from typing import Union

import numpy as np


simio_data_types = {
    'StringState': str,
    'DateTimeState': datetime.datetime,
    'DiscreteState': float,
    'BooleanState': bool,
    'ElementReferenceState': str,
    'IntegerState': int}


def get_project_folder_name(project_file_name: str) -> str:
    """
    Get the name of a folder associated with a project.
    :param project_file_name: Name of the project.
    :return: Name of the project folder according to Simio's nomenclature.
    """
    project_name = project_file_name.split('.')[0]
    folder_name = '.'.join([project_name, 'Files'])
    return folder_name


def extract_list_from_dom(dom_object: minidom.Document,
                          tag_name: Union[str, None] = None,
                          attribute_name: str = None,
                          prefix_str: str = str(),
                          suffix_str: str = str()) -> list:
    """
    Extract a list of DOM or strings from a dom, filtering by tag name.
    :param dom_object: DOM Parent.
    :param tag_name: Tag to filter. Compulsory because DOM is primarily filtered by this UNLESS it has already filtered.
    :param attribute_name: If you want to get a list of sub-doms, set this parameter to None.
    :param prefix_str: If you want to get a String, this add a prefix string fragment.
    :param suffix_str: If you want to get a String, this add a suffix string fragment.
    :return: List of DOMs or strings.
    """
    if tag_name is None:
        dom_from_tag = dom_object
    else:
        dom_from_tag = dom_object.getElementsByTagName(tag_name)
    if attribute_name is None:
        list_results = [item for item in dom_from_tag]
    else:
        try:
            list_results = [prefix_str+item.attributes[attribute_name].value+suffix_str for item in dom_from_tag]
        except AttributeError:
            list_results = [np.NaN]
    return list_results


def filter_dom_by_attribute(list_of_doms: list,
                            attribute_name: str,
                            attribute_value: str) -> list:
    """
    Filter DOM by attribute value.
    :param list_of_doms:
    :param attribute_name:
    :param attribute_value:
    :return: filtered list of DOM.
    """
    list_models = [item for item in list_of_doms if item.attributes[attribute_name].value == attribute_value]
    if len(list_models) == 0:
        warnings.warn(f'No {attribute_name} with value {attribute_value} has been found.')
        return [np.NaN]
    else:
        return list_models


def get_model_from_list_of_doms(list_of_doms: list,
                                model_name: str) -> minidom.Document:
    """
    Provided a list of models from a .simproj, this function selects a model named as model_name.
    :param list_of_doms: list of simio models in a .simproj.
    :param model_name: Name of the model to be selected.
    :return: Model named model_name
    """
    list_models = [item for item in list_of_doms if item.attributes['Definition'].value == model_name]
    if len(list_models) == 0:
        raise ValueError(f'No model with name {model_name} has been found.')
    elif len(list_models) > 1:
        raise ValueError(f'There is more than one model with name {model_name}.')
    else:
        return list_models[0]
