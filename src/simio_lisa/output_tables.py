import datetime
import os
import pandas as pd
from simio_lisa.utils import *
from simio_lisa.load_simio_project import get_model_metadata, get_model_tables_path, get_output_table_names, get_input_table_names


class OutputTable:
    def __init__(self, model_metadata, table_path: str):
        self.__model_metadata = model_metadata
        self.__table_path = table_path
        self.__table_schema = self.load_schema(self.__model_metadata)

    def load_schema(self, model_metadata):
        """
        Load data types of columns.
        :param model_metadata:
        :return: Dictionary mapping column name -> data type
        """
        list_tables = extract_list_from_dom(dom_object=model_metadata, tag_name='Table')
        attribute_value = self.table_path.split(os.path.sep)[-1].split('.')[0]
        dom_tables = filter_dom_by_attribute(list_of_doms=list_tables,
                                             attribute_name='Name',
                                             attribute_value=attribute_value)[0]
        metadata_results = dict()
        for simio_data_type, python_data_type in simio_data_types.items():
            column_names = extract_list_from_dom(dom_object=dom_tables,
                                                 tag_name=simio_data_type,
                                                 attribute_name='Name')
            for col in column_names:
                metadata_results[col] = python_data_type
        return metadata_results

    @staticmethod
    def get_single_row_value(dom_row_list: list):
        """
        Get value of a single scenario's response.
        :param dom_row_list: Single row provided as a list of one term.
        :return: Value of such observation.
        """
        row_list = extract_list_from_dom(dom_object=dom_row_list,
                                         attribute_name='Value')
        if len(row_list) == 0:
            response_value = np.NaN
        else:
            response_value = row_list[0]
        return response_value

    @staticmethod
    def get_input_single_row_value(dom_row_list: list):
        """
        Get value of a single scenario's response.
        :param dom_row_list: Single row provided as a list of one term.
        :return: Value of such observation.
        """
        tag_value = 'Value'
        response = dom_row_list[0]
        if pd.isna(response):
            response_value = np.NaN
        elif len(response.getElementsByTagName(tag_value))>0:
            response_value = response.getElementsByTagName(tag_value)[0].childNodes[0].data
        else:
            response_value = response.childNodes[0].data
        return response_value

    def add_row_to_table(self,
                         result_dict: dict,
                         dom_row: minidom.Document,
                         column_names: set):
        """
        Load row to table
        :param result_dict: Dictionary of results to be updated.
        :param dom_row: List of.
        :param column_names: Set of response names to iterate over.
        :return: Nothing. Result dictionary is updated
        """
        row = dom_row.getElementsByTagName('StateValue')
        for resp in column_names:
            response = filter_dom_by_attribute(list_of_doms=row,
                                               attribute_name='Name',
                                               attribute_value=resp)
            value_response = self.get_single_row_value(dom_row_list=response)
            result_dict[resp].append(value_response)

    def add_row_to_input_table(self,
                         result_dict: dict,
                         dom_row: minidom.Document,
                         column_names: set,
                         tag_name = 'StateValue',
                         attribute_name = 'Name'
                               ):
        """
        Load row to table
        :param result_dict: Dictionary of results to be updated.
        :param dom_row: List of.
        :param column_names: Set of response names to iterate over.
        :return: Nothing. Result dictionary is updated
        """
        row = dom_row.getElementsByTagName(tag_name)
        for resp in column_names:
            response = filter_dom_by_attribute(list_of_doms=row,
                                               attribute_name=attribute_name,
                                               attribute_value=resp)
            value_response = self.get_input_single_row_value(dom_row_list=response)
            result_dict[resp].append(value_response)

    @staticmethod
    def get_column_names(row_doms, tag_name='StateValue', attribute_name='Name'):
        column_names = list()
        for i in row_doms:
            column_names.extend(extract_list_from_dom(dom_object=i,
                                                      tag_name=tag_name,
                                                      attribute_name=attribute_name))
        column_names = set(column_names)
        return column_names

    def load_single_output_table(self) -> Union[pd.DataFrame, None]:
        """
        Load results of single experiment
        :return: DataFrame with result of experiment.
        """
        try:
            project_xml = minidom.parse(self.table_path)
        except FileNotFoundError:
            warnings.warn(f'Table {self.table_path} has not been ran yet.')
            return None
        row_doms = extract_list_from_dom(dom_object=project_xml,
                                         tag_name='Row')
        if len(row_doms) == 0:
            warnings.warn(f'Table {self.table_path} is empty')
            return None
        column_names = self.get_column_names(row_doms=row_doms)
        results_dict = {col: [] for col in column_names}
        for row in row_doms:
            self.add_row_to_table(result_dict=results_dict,
                                  dom_row=row,
                                  column_names=column_names)
        results_df = pd.DataFrame(results_dict)
        results_df = self.apply_data_type(results_df)
        return results_df

    def load_single_table(self) -> Union[pd.DataFrame, None]:
        """
        Load results of single experiment
        :return: DataFrame with result of experiment.
        """
        try:
            project_xml = minidom.parse(self.table_path)
        except FileNotFoundError:
            warnings.warn(f'Table {self.table_path} has not been ran yet.')
            return None
        row_doms = extract_list_from_dom(dom_object=project_xml,
                                         tag_name='Row')
        if len(row_doms) == 0:
            warnings.warn(f'Table {self.table_path} is empty')
            return None
        tag_name = 'Property'
        attribute_name = 'Name'
        column_names = self.get_column_names(row_doms=row_doms, tag_name=tag_name, attribute_name=attribute_name)
        results_dict = {col: [] for col in column_names}
        for row in row_doms:
            self.add_row_to_input_table(result_dict=results_dict,
                                        dom_row=row,
                                        column_names=column_names,
                                        tag_name=tag_name,
                                        attribute_name=attribute_name)
        results_df = pd.DataFrame(results_dict)
        results_df = self.apply_data_type(results_df)
        return results_df

    def apply_data_type(self, results_df):
        for col, val in self.table_schema.items():
            if val in [int, float, bool]:
                results_df[col] = results_df[col].astype(val)
            elif val == datetime.datetime:
                results_df[col] = pd.to_datetime(results_df[col])
            elif val == str:
                pass
            else:
                raise NotImplementedError(f'{val} is not a recognized data type.')

        return results_df

    # Getters and setters
    @property
    def model_metadata(self):
        return self.__model_metadata

    @model_metadata.setter
    def model_metadata(self, model_metadata):
        self.__model_metadata = model_metadata

    @property
    def table_path(self):
        return self.__table_path

    @table_path.setter
    def table_path(self, table_path: str):
        self.__table_path = table_path

    @property
    def table_schema(self):
        return self.__table_schema

    @table_schema.setter
    def table_schema(self, table_schema: str):
        self.__table_schema = table_schema


class OutputTables:
    def __init__(self,
                 path_to_project: str,
                 model_file_name: str,
                 model_name: str):
        self.__model_metadata = get_model_metadata(path_to_project=path_to_project,
                                                   model_file_name=model_file_name,
                                                   model_name=model_name)
        self.__tables_path = get_model_tables_path(project_path=path_to_project,
                                                   project_filename=model_file_name,
                                                   model_name=model_name)
        self.__output_file_list = get_output_table_names(output_table_path=self.__tables_path)
        self.__input_file_list = get_input_table_names(input_table_path=self.__tables_path)

        self.__output_tables = None
        self.__input_tables = None

    def load_output_tables(self):
        """
            Load all experiment results related to a Simio model.
            :return: Dictionary whose keys are experiment name and value is a data frame (or None).
            """
        experiment_dictionary = dict()
        for _table_name in self.output_file_list:
            table_path = os.path.join(self.tables_path, _table_name)
            output_table = OutputTable(model_metadata=self.model_metadata,
                                       table_path=table_path)
            experiment_dictionary[_table_name.split('.')[0]] = output_table.load_single_output_table()
        self.output_tables = experiment_dictionary

    def load_input_tables(self):
        """
            Load all experiment results related to a Simio model.
            :return: Dictionary whose keys are experiment name and value is a data frame (or None).
            """
        experiment_dictionary = dict()
        for _table_name in self.input_file_list:
            table_path = os.path.join(self.tables_path, _table_name)
            input_table = OutputTable(model_metadata=self.model_metadata,
                                       table_path=table_path)
            experiment_dictionary[_table_name.split('.')[0]] = input_table.load_single_table()
        self.input_tables = experiment_dictionary

    # Getters and Setters
    @property
    def model_metadata(self):
        return self.__model_metadata

    @model_metadata.setter
    def model_metadata(self,
                       model_metadata_xml):
        self.__model_metadata = model_metadata_xml

    @property
    def tables_path(self):
        return self.__tables_path

    @tables_path.setter
    def tables_path(self,
                    path_to_tables: str):
        self.__tables_path = path_to_tables

    @property
    def output_file_list(self):
        return self.__output_file_list

    @output_file_list.setter
    def output_file_list(self,
                         tables_path: str):
        self.__output_file_list = get_output_table_names(output_table_path=tables_path)

    @property
    def input_file_list(self):
        return self.__input_file_list

    @input_file_list.setter
    def input_file_list(self,
                         tables_path: str):
        self.__input_file_list = get_input_table_names(input_table_path=tables_path)

    @property
    def input_tables(self):
        return self.__input_tables

    @input_tables.setter
    def input_tables(self,
               input_tables: dict):
        self.__input_tables = input_tables

    @property
    def output_tables(self):
        return self.__output_tables

    @output_tables.setter
    def output_tables(self,
               output_tables: dict):
        self.__output_tables = output_tables

if __name__ == '__main__':
    path_output_tables = os.path.normpath(os.environ['PATHOUTPUTTABLES'])
    project_path = os.path.normpath(os.environ['SIMIOPROJECTPATH'])
    project_name = os.environ['SIMIOPROJECTNAME']
    model_name = os.environ['MODELNAME']

    output_tables_ = OutputTables(path_to_project=project_path,
                                  model_file_name=project_name,
                                  model_name=model_name)

    output_tables_.load_input_tables()
    print()


    import xml.etree.ElementTree as ET
    tree = ET.parse(
        r'C:\Users\alessandro.seri\Documents\GitHub\mars_retort_02_model\SeizeApproach_V2\Seize Approach V2.Files\Models\Model\TableData\ArrivalTableFlex.xml')
    root = tree.getroot()
    for rows in root.findall('Row'):
        prop = rows.find('Properties')
        for v in prop.findall('Property'):
            print(v.text)

    tree = minidom.parse(
        r'C:\Users\alessandro.seri\Documents\GitHub\mars_retort_02_model\SeizeApproach_V2\Seize Approach V2.Files\Models\Model\TableData\ArrivalTableFlex.xml')
    for t in tree.getElementsByTagName('Row'):
        print(t)
        a = t.getElementsByTagName('Properties')
        for p in a[0].getElementsByTagName('Property'):
            print(p.getAttribute('Name'), p.childNodes[0].data)

    # 'Property' = t.getElementsByTagName(t.childNodes[1].localName)[0].childNodes[1].localName


    a[0].getElementsByTagName('Property')[0].childNodes[0].data


    # types
    for table in output_tables_.input_file_list:
        table = table.split('.')[0]
        dom_tables = filter_dom_by_attribute(list_of_doms=list_tables,
                                         attribute_name='Name',
                                         attribute_value=table)[0]
        print(dom_tables.getElementsByTagName('PropertyDefinitions')[0].childNodes)

    pass
