from simio_lisa.load_simio_project import *
from simio_lisa.output_tables import *
import logging
import copy
import pandas as pd
import numpy as np
import os.path
import os
import datetime
import matplotlib.pyplot as plt
import runpy
import plotly.express as px
from plotly.offline import plot
import time
from abc import ABC, abstractmethod
import plotly.graph_objects as go
from plotly.subplots import make_subplots
class SimioKpis(ABC):
    def __init__(self,
                 logger_level: str = logging.INFO,
                 **kwargs):
        """
        Parent class.
        :param output_tables: DICT containing all tables
        :param **
        :param **
        :param **
        """
        # Instance Tables
        self._tables = kwargs.get('tables', None)
        self._mode_kpi = kwargs.get('mode_kpi', None)
        self._title_kpi = kwargs.get('title_kpi', None)
        self._value_kpi = kwargs.get('value_kpi', None)
        self._row_cols = kwargs.get('row_cols', None)
        self._reference_kpi = kwargs.get('reference_kpi', None)

        logging.getLogger().setLevel(logger_level)

    def plot(self):
        fig = go.Figure()
        if type(self.mode_kpi) is str:
            fig.add_trace(go.Indicator(
                mode=self.mode_kpi,
                value=self.value_kpi,
                title=self.title_kpi,
                delta={'reference': self.reference_kpi, 'relative': True}
                        ))
        else:
            row_cols_combi = [[i, ii] for i in np.arange(0,self.row_cols[0],1) for ii in np.arange(0,self.row_cols[1],1)]
            for (mk, vk, tk, rk, row_colk) in zip(self.mode_kpi, self.value_kpi, self.title_kpi, self.reference_kpi, row_cols_combi):
                fig.add_trace(go.Indicator(
                    mode=mk,
                    value=vk,
                    title=tk,
                    delta={'reference': rk, 'relative': True},
                    gauge={
                        'axis': {'visible': False}},
                    domain={'row': int(row_colk[0]), 'column': int(row_colk[1])}
                            ))
        fig.update_layout(
            grid={'rows': self.row_cols[0], 'columns': self.row_cols[1], 'pattern': "independent"}
            )
        return fig

    def calculate(self, kpi_dict):
        result = {}
        for k in kpi_dict.keys():
            col = self.tables[kpi_dict[k]['table']][kpi_dict[k]['column']]
            if kpi_dict[k]['operation'] == 'sum':
                kpi = col.sum()
            elif kpi_dict[k]['operation'] == 'mean':
                kpi = col.mean()
            elif kpi_dict[k]['operation'] == 'min':
                kpi = col.min()
            elif kpi_dict[k]['operation'] == 'count_unique':
                kpi = len(col.unique())
            elif kpi_dict[k]['operation'] == 'count_events':
                kpi = len(col)
            else:
                raise ValueError(f'Operation {kpi_dict[k]["operation"]} is not defined.')
            result[kpi_dict[k]['label']] = kpi
        return result

    @property
    def tables(self):
        return self._tables

    @property
    def tables_names(self):
        return self._tables_names

    @property
    def title_kpi(self):
        return self._title_kpi

    @title_kpi.setter
    def title_kpi(self, new_value):
        self._title_kpi = new_value

    @property
    def mode_kpi(self):
        return self._mode_kpi

    @mode_kpi.setter
    def mode_kpi(self, new_value):
        self._mode_kpi = new_value

    @property
    def value_kpi(self):
        return self._value_kpi

    @value_kpi.setter
    def value_kpi(self, new_value):
        self._value_kpi = new_value

    @property
    def reference_kpi(self):
        return self._reference_kpi

    @reference_kpi.setter
    def reference_kpi(self, new_value):
        self._reference_kpi = new_value

    @property
    def row_cols(self):
        return self._row_cols

    @row_cols.setter
    def row_cols(self, new_value):
        self._row_cols = new_value



if __name__ == '__main__':

    # operations:
    print('1 kpi')
    nuovo = SimioKpis(mode_kpi = 'number+delta', value_kpi = 450, title_kpi = 'a',
                    row_cols = [1, 1], reference_kpi = 400)
    fig = nuovo.plot()
    plot(fig)

    print('many kpis')
    mode_kpi_v = ['number+delta', 'number+delta', 'number', 'number']
    value_kpi_v = [450, 210, 130, 400]
    title_kpi_v = ['a', 'b', 'c', 'd']
    row_cols_v = [2, 2]
    reference_kpi_v = [400, 300, 400, 400]

    nuovo = SimioKpis(mode_kpi = mode_kpi_v, value_kpi = value_kpi_v, title_kpi = title_kpi_v,
                    row_cols = row_cols_v, reference_kpi =reference_kpi_v)

    print('Extract KPIs from tables and plot them')
    output_tables = OutputTables()
    output_tables_new = output_tables.tables
    # Add filtered tables for specific KPI calculations
    output_tables_new['OutputObjectUtilization_PickUpShuttle'] = output_tables_new['OutputObjectUtilization'][output_tables_new[
                                                                        'OutputObjectUtilization'].ObjectId == 'PickUpShuttle[1]']
    # Calculate kpis
    # All tables(['OutputFailures', 'OutputLoadingUnloadingTimes', 'OutputObjectUtilization',
    # 'OutputPalletProcessing', 'OutputProductArrivals', 'OutputProductDeparture', 'OutputRetortProcessing',
    # 'OutputShuttleLocations', 'OutputShuttlePickUps', 'OutputStatus5A', 'OutputStatus5B', 'OutputStatus6'])
    # All operations: max, min, mean, count_events, count_unique
    table_name1 = 'OutputFailures'
    column_name1 = 'FailureID'
    operation_name1 = 'count_unique'
    label1 = 'Number of Retorts Failures'
    table_name12 = 'OutputFailures'
    column_name12 = 'ObjectName'
    operation_name12 = 'count_unique'
    label12 = 'Number of Retorts'
    table_name21 = 'OutputProductArrivals'
    column_name21 = 'TimeBeforePicking'
    operation_name21 = 'mean'
    label21 = 'Cubes average time in line'
    table_name22 = 'OutputObjectUtilization_PickUpShuttle'
    column_name22 = 'TimeDown'
    operation_name22 = 'sum'
    label22 = 'Failures PickUp Shuttle'
    input_dict = {
        'kpi1': {'table': table_name1,
                 'column': column_name1,
                 'operation': operation_name1,
                 'label': label1},
        'kpi2': {'table': table_name12,
                 'column': column_name12,
                 'operation': operation_name12,
                 'label': label12},
        'kpi3': {'table': table_name21,
                 'column': column_name21,
                 'operation': operation_name21,
                 'label': label21},
        'kpi4': {'table': table_name22,
                 'column': column_name22,
                 'operation': operation_name22,
                 'label': label22}
        }

    KPIs = nuovo.calculate(input_dict)
    nuovo._value_kpi = [KPIs[i] for i in KPIs.keys()]
    nuovo._title_kpi = [i for i in KPIs.keys()]
    nuovo._row_cols=[1, len(KPIs.keys())]
    nuovo._reference_kpi = [100, 0, 5*60/3600, 0]
    nuovo._mode_kpi = ['number+delta', 'number', 'number+delta', 'number']
    # add increasing or dicreasing on KPI with number+delta
    # https://plotly.com/python/gauge-charts/
    fig = nuovo.plot()
    plot(fig)