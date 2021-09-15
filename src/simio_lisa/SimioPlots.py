from simio_lisa.load_simio_project import *
import logging
import copy
import pandas as pd
import numpy as np
import os.path
import datetime
import matplotlib.pyplot as plt
import runpy
import plotly.express as px
from plotly.offline import plot
import time


class SimioPlotter:
    def __init__(self,
                 project_path: str,
                 project_name: str,
                 model_name: str,
                 path_output_tables: str,
                 logger_level: str = logging.INFO,
                 **kwargs):
        """

        :param project_path:
        :param project_name:
        :param project_path:
        :param model_name:
        """
        self._tables_names = get_output_table_names(path_output_tables)
        self._tables = None
        # Instance Tables
        self._x_axis = kwargs.get('x_axis', None)
        self._y_axis = kwargs.get('y_axis', None)
        self._time_axis = kwargs.get('time_axis', None)
        self._objects_dict = kwargs.get('objects_dict', None)
        object_groups_dict = kwargs.get('objects_dict', None)

        logging.getLogger().setLevel(logger_level)

    def get_tables(self):
        self._tables = load_output_tables(project_path, project_name, model_name)

 #   Convert input data
    def plot(self, tables, kind):
        """
        Import dim_object_properties from data_model and creates a table with all the objects containing all their properties: location, processing times, loading/unloading times, ...
        The object type is also added importing dim_objects.
        """
        if kind == 'time_series_columns':
            simio_ts_plotter = SimioTimeSeries(
                                project_path,
                                project_name,
                                model_name,
                                path_output_tables,
                                logging.INFO,
                                time_axis=self.time_axis,
                                y_axis=self.y_axis
                                )
            if simio_ts_plotter.tables == None:
                simio_ts_plotter.get_tables()
            fig = simio_ts_plotter.plot_columns(table=tables)
            fig.show()
            plot(fig)
        elif kind== 'time_series_tables':
            simio_ts_plotter = SimioTimeSeries(
                                project_path,
                                project_name,
                                model_name,
                                path_output_tables,
                                logging.INFO,
                                time_axis=self.time_axis,
                                y_axis=self.y_axis
                                )
            if simio_ts_plotter.tables == None:
                simio_ts_plotter.get_tables()
            fig = simio_ts_plotter.plot_tables(tables=tables)
            fig.show()
            plot(fig)
        elif kind == 'bars_object_utilization':
            simio_ou_plotter = SimioObjUtilization(project_path,
                                                   project_name,
                                                   model_name,
                                                   path_output_tables,
                                                   x_axis=self.x_axis,
                                                   y_axis=self.y_axis,
                                                   objects_dict=self.objects_dict)
            if simio_ou_plotter.tables == None:
                simio_ou_plotter.get_tables()
            fig = simio_ou_plotter.plot_bars(tables = tables)
            for k in fig.keys():
                fig[k].show()
                plot(fig[k])
        elif kind == 'pie_object_utilization':
            simio_ou_plotter = SimioObjUtilization(project_path,
                                                   project_name,
                                                   model_name,
                                                   path_output_tables,
                                                   x_axis=self.x_axis,
                                                   y_axis=self.y_axis,
                                                   objects_dict=self.objects_dict)
            if simio_ou_plotter.tables == None:
                simio_ou_plotter.get_tables()
            fig = simio_ou_plotter.plot_pie(tables = tables)
            for k in fig.keys():
                fig[k].show()
                plot(fig[k])
        elif kind == 'bars_time_series_object_utilization':
            simio_ou_plotter = SimioObjUtilization(project_path,
                                                   project_name,
                                                   model_name,
                                                   path_output_tables,
                                                   x_axis=self.x_axis,
                                                   y_axis=self.y_axis,
                                                   time_axis=self.time_axis,
                                                   objects_dict=self.objects_dict)
            if simio_ou_plotter.tables == None:
                simio_ou_plotter.get_tables()
            fig = simio_ou_plotter.plot_bars_time_series(tables = tables)
            print(fig)
            for k in fig.keys():
                print(k)
                fig[k].show()
                plot(fig[k])
        else:
            raise MissingKindError(f'Kind {kind} not defined')


    @property
    def tables(self):
        return self._tables

    @property
    def tables_names(self):
        return self._tables_names

    @property
    def time_axis(self):
        return self._time_axis

    @property
    def y_axis(self):
        return self._y_axis

    @property
    def x_axis(self):
        return self._x_axis

    @property
    def objects_dict(self):
        return self._objects_dict


class SimioTimeSeries(SimioPlotter):
    def __init__(self,
                 project_path: str,
                 project_name: str,
                 model_name: str,
                 path_output_tables: str,
                 logger_level: str = logging.INFO,
                 **kwargs):
        """

        :param project_path:
        :param project_name:
        :param project_path:
        :param model_name:
        """
        SimioPlotter.__init__(self,
                              project_path,
                              project_name,
                              model_name,
                              path_output_tables,
                              logging.INFO,
                              **kwargs)

    def plot_columns(self, table: str):
        """
        Plot TimeSeries comparing different columns (y_Axis should be a list of columns, only one table should be provided)
        :param all_tables_attribute:
        :param table:
        :param time_axis:
        :param y_axis:
        :return:
        """
        input_data = self.tables[table]
        time_axis = self.time_axis
        y_axis = self.y_axis

        input_data[time_axis] = pd.to_datetime(input_data[time_axis])
        fig = px.line(input_data, x=time_axis, y=y_axis)
        return fig

    def plot_tables(self, tables):
        """
        Plot TimeSeries comparing different tables (time_axis and y_axis should have the same name in all the tables)
        :param all_tables_attribute:
        :param tables:
        :param time_axis:
        :param y_axis:
        :return:
        """
        if type(tables) is str:
            input_data = self.tables[tables]
            input_data['source'] = tables
        else:
            input_data = pd.DataFrame()
            for t in tables:
                aux = self.tables[t]
                aux['source'] = t
                input_data = input_data.append(aux, ignore_index=True)
        time_axis = self.time_axis
        y_axis = self.y_axis

        input_data[time_axis] = pd.to_datetime(input_data[time_axis])

        fig = px.line(input_data, x=time_axis, y=y_axis, color='source')
        return fig

class SimioObjUtilization(SimioPlotter):
    def __init__(self,
                 project_path: str,
                 project_name: str,
                 model_name: str,
                 path_output_tables: str,
                 **kwargs):
        """

        :param project_path:
        :param project_name:
        :param project_path:
        :param model_name:
        :param objects_dict: dictionary grouping the objects to compare
        """
        SimioPlotter.__init__(self,
                              project_path,
                              project_name,
                              model_name,
                              path_output_tables,
                              logging.INFO,
                              **kwargs)

    def plot_bars(self, tables: str):

        if type(tables) is str:
            input_data = self.tables[tables]
            input_data['source'] = tables
        else:
            input_data = pd.DataFrame()
            for t in tables:
                aux = self.tables[t]
                aux['source'] = t
                input_data = input_data.append(aux, ignore_index=True)
        y_axis = self.y_axis
        x_axis = self.x_axis
        object_groups_dict = self.objects_dict
        input_data[y_axis] = input_data[y_axis].astype(float) #otherwise the column is lost when grouping

        f = {}
        for k in object_groups_dict.keys():
            input_data_plt = input_data[input_data[x_axis].isin(object_groups_dict[k])].copy(deep=True)
            input_data_plt = input_data_plt.groupby(by=x_axis, as_index=False).mean()
            fig = px.bar(input_data_plt, x=x_axis, y=y_axis, barmode="group")
            f[k] = fig
        return f

    def plot_pie(self, tables: str):

        if type(tables) is str:
            input_data = self.tables[tables]
            input_data['source'] = tables
        else:
            input_data = pd.DataFrame()
            for t in tables:
                aux = self.tables[t]
                aux['source'] = t
                input_data = input_data.append(aux, ignore_index=True)
        y_axis = self.y_axis
        x_axis = self.x_axis
        object_groups_dict = self.objects_dict
        input_data[y_axis] = input_data[y_axis].astype(float) #otherwise the column is lost when grouping

        f = {}
        for k in object_groups_dict.keys():
            input_data_plt = input_data[input_data[x_axis].isin(object_groups_dict[k])].copy(deep=True)
            input_data_plt = input_data_plt.groupby(by=x_axis, as_index=False).mean()
            fig = px.pie(input_data_plt, values=y_axis, names=x_axis,
                          title=x_axis + ' utilization quantified in terms of ' + y_axis + ', group ' + k)
            f[k] = fig
        return f

    def plot_bars_time_series(self, tables: str):

        if type(tables) is str:
            input_data = self.tables[tables]
            input_data['source'] = tables
        else:
            input_data = pd.DataFrame()
            for t in tables:
                aux = self.tables[t]
                aux['source'] = t
                input_data = input_data.append(aux, ignore_index=True)
        y_axis = self.y_axis
        x_axis = self.x_axis
        time_axis = self.time_axis
        object_groups_dict = self.objects_dict
        input_data[y_axis] = input_data[y_axis].astype(float) #otherwise the column is lost when grouping

        f = {}
        for k in object_groups_dict.keys():
            input_data_plt = input_data[input_data[x_axis].isin(object_groups_dict[k])].copy(deep=True)
            fig = px.bar(input_data_plt, x=x_axis, y=y_axis, barmode="group", facet_col=time_axis)
            f[k] = fig
        return f


if __name__ == '__main__':
    path_output_tables = os.path.normpath(r'C:\Users\alessandro.seri\Accenture\MARS Retort MVP - AI - General\02_Data\03_output_data\01_raw_data\scenarios\MicroStops_0')
    output_tables_names = get_output_table_names(path_output_tables)

    project_path = os.path.normpath(r'C:\Users\alessandro.seri\Documents\GitHub\mars_retort_02_model\SeizeApproach_V2')
    project_name = 'Seize Approach V2.simproj'
    model_name = 'Model'

    object_groups_dict = {'Shuttles': ['DropOffShuttle[1]', 'PickUpShuttle[1]'],
                          'Retorts': ['Retort1', 'Retort2', 'Retort3', 'Retort4',
                                      'Retort5', 'Retort6', 'Retort7', 'Retort8',
                                      'Retort9', 'Retort10']
                          }
    x_axis = 'ObjectId'
    y_axis = 'Utilization'
    time_axis = 'DateTime'
    simio_plotter_class = SimioPlotter(
                 project_path,
                 project_name,
                 model_name,
                 path_output_tables,
                 logging.INFO,
                 x_axis = x_axis, y_axis= y_axis,
                 time_axis=time_axis
                 objects_dict=object_groups_dict)

    print('Time Series plots')
    # for this one y_axis should be 'Utilization', time_axis = 'DateTime'
    simio_plotter_class._time_axis = 'DateTime'
    simio_plotter_class._y_axis = 'Utilization'
    simio_plotter_class.plot(tables='OutputObjectUtilization', kind='time_series_columns')
    # for this one y_axis should be 'Count', time_axis = 'StatusDate'
    simio_plotter_class._time_axis = 'StatusDate'
    simio_plotter_class._y_axis = 'Count'
    simio_plotter_class.plot(tables=['OutputStatus5A', 'OutputStatus5B', 'OutputStatus6'], kind='time_series_tables')

    print('Object Utilization')
    # for this one x_axis = 'ObjectId', y_axis='Utilization'
    simio_plotter_class._x_axis = 'ObjectId'
    simio_plotter_class._y_axis = 'Utilization'
    simio_plotter_class._object_dict = object_groups_dict
    simio_plotter_class.plot(tables='OutputObjectUtilization', kind='bars_object_utilization')
    simio_plotter_class.plot(tables='OutputObjectUtilization', kind='pie_object_utilization')

    simio_plotter_class._time_axis = 'DateTime'
    simio_plotter_class.plot(tables='OutputObjectUtilization', kind='bars_time_series_object_utilization')

