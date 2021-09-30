from simio_lisa.simio_tables import *
import logging
import pandas as pd
import os
import plotly.express as px
from plotly.offline import plot
import time
from abc import ABC, abstractmethod


class SimioPlotter(ABC):
    def __init__(self,
                 output_tables,
                 logger_level: int = logging.INFO,
                 **kwargs):
        """
        Parent class.
        :param output_tables: DICT containing all tables
        :param **x_axis/y_axis/time_axis: column to be used as x/y/time axis
        :param **legend_col: column to use to distinguish colors/legend
        :param **objects_dict: dictionary to distinguish the groups of entities to be compared together
        """
        self._tables_names = None
        self._tables = output_tables
        # Instance Tables
        self._x_axis = kwargs.get('x_axis', None)
        self._y_axis = kwargs.get('y_axis', None)
        self._time_axis = kwargs.get('time_axis', None)
        self._objects_dict = kwargs.get('objects_dict', None)
        self._legend_col = kwargs.get('legend_col', None)

        logging.getLogger().setLevel(logger_level)

    @abstractmethod
    def plot(self, tables, kind):
        """
        Force all subclasses to have a plot method
        """
        pass

    @property
    def tables(self):
        return self._tables

    @property
    def tables_names(self):
        return self._tables_names

    @property
    def time_axis(self):
        return self._time_axis

    @time_axis.setter
    def time_axis(self, new_value):
        self._time_axis = new_value

    @property
    def y_axis(self):
        return self._y_axis

    @y_axis.setter
    def y_axis(self, new_value):
        self._y_axis = new_value

    @property
    def x_axis(self):
        return self._x_axis

    @x_axis.setter
    def x_axis(self, new_value):
        self._x_axis = new_value

    @property
    def objects_dict(self):
        return self._objects_dict

    @objects_dict.setter
    def objects_dict(self, new_value):
        self._objects_dict = new_value

    @property
    def legend_col(self):
        return self._legend_col

    @legend_col.setter
    def legend_col(self, new_value):
        self._legend_col = new_value


class SimioTimeSeries(SimioPlotter):
    def __init__(self,
                 output_tables,
                 logger_level: int = logging.INFO,
                 **kwargs):
        """
        Class child of SimioPlotter to plot time series. Necessary in kwargs: time_axis and y_axis.
        When using plot_columns (plot_tables) y_axis (tables) can be a list.
        """
        SimioPlotter.__init__(self,
                              output_tables,
                              logger_level,
                              **kwargs)

    def plot_columns(self, table: str):
        """
        Plot TimeSeries comparing different columns (y_Axis should be a list of columns,
        only one table should be provided)
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
        :param tables:
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

    def plot(self, tables, kind):
        if kind == 'time_series_columns':
            fig = self.plot_columns(table=tables)
            plot(fig)
        elif kind == 'time_series_tables':
            fig = self.plot_tables(tables=tables)
            plot(fig)
        else:
            raise ValueError(f'Kind {kind} not defined')


class SimioBarPie(SimioPlotter):
    def __init__(self,
                 output_tables,
                 logger_level: int = logging.INFO,
                 **kwargs):
        """
        Class child of SimioPlotter to plot bar plots or pie charts. Necessary in kwargs: x_axis, y_axis and
        objects_dict (time_axis necessary only for method plot_bars_time_series)
        :param objects_dict: dictionary grouping the objects to compare
        """
        SimioPlotter.__init__(self,
                              output_tables,
                              logger_level,
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
        input_data[y_axis] = input_data[y_axis].astype(float)  # otherwise the column is lost when grouping

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
        input_data[y_axis] = input_data[y_axis].astype(float)  # otherwise the column is lost when grouping

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
        input_data[time_axis] = input_data[time_axis].astype(str)
        input_data[y_axis] = input_data[y_axis].astype(float)  # otherwise the column is lost when grouping

        f = {}
        for k in object_groups_dict.keys():
            input_data_plt = input_data[input_data[x_axis].isin(object_groups_dict[k])].copy(deep=True)
            fig = px.bar(input_data_plt, x=x_axis, y=y_axis, barmode="group", facet_col=time_axis)
            f[k] = fig
        return f

    def plot(self, tables, kind):
        if kind == 'bars_plot':
            fig = self.plot_bars(tables=tables)
            for k in fig.keys():
                plot(fig[k])
                time.sleep(.5)
        elif kind == 'pie_plot':
            fig = self.plot_pie(tables=tables)
            for k in fig.keys():
                plot(fig[k])
                time.sleep(.5)
        elif kind == 'bars_time_series_plot':
            fig = self.plot_bars_time_series(tables=tables)
            for k in fig.keys():
                plot(fig[k])
                time.sleep(.5)
        else:
            raise ValueError(f'Kind {kind} not defined')


class SimioBox(SimioPlotter):
    def __init__(self,
                 output_tables,
                 logger_level: int = logging.INFO,
                 **kwargs):
        """

        :param project_path:
        :param project_name:
        :param project_path:
        :param model_name:
        """
        SimioPlotter.__init__(self,
                              output_tables,
                              logger_level,
                              **kwargs)

    def plot_box(self, tables):
        """
        Class child of SimioPlotter to plot box plots. Necessary in kwargs: x_axis and y_axis.
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
        x_axis = self.x_axis
        y_axis = self.y_axis
        fig = px.box(input_data, x=x_axis, y=y_axis, color=x_axis, notched=True)
        return fig

    def plot(self, tables, kind):
        if kind == 'box_plot':
            fig = self.plot_box(tables=tables)
            plot(fig)
        else:
            raise ValueError(f'Kind {kind} not defined')


class SimioStackedBars(SimioPlotter):
    def __init__(self,
                 output_tables,
                 logger_level: int = logging.INFO,
                 **kwargs):
        """
        Class child of SimioPlotter to plot stacked bars. Necessary in kwargs: x_axis, y_axis and legend_col.
        """
        SimioPlotter.__init__(self,
                              output_tables,
                              logger_level,
                              **kwargs)

    def plot_stacked_bars(self, tables):
        if type(tables) is str:
            input_data = self.tables[tables]
            input_data['source'] = tables
        else:
            input_data = pd.DataFrame()
            for t in tables:
                aux = self.tables[t]
                aux['source'] = t
                input_data = input_data.append(aux, ignore_index=True)
        x_axis = self.x_axis
        y_axis = self.y_axis
        legend_col = self.legend_col
        fig = px.bar(input_data, x=x_axis, y=y_axis, color=legend_col)
        return fig

    def plot(self, tables, kind):
        if kind == 'stacked_bars':
            fig = self.plot_stacked_bars(tables=tables)
            plot(fig)
        else:
            raise ValueError(f'Kind {kind} not defined')


def create_object_processing_table(tables):
    """
    Create a table with all the processes 'operation' happening to each entity 'object_id' and their durations extracted
     from 'start' and 'stop' columns.
    The processes come from two different tables defined in "operation1""table" and "operation2""table"
    :param tables: DICT
    :return: tables DICT (with the new table added with name "ObjectProcessingTable"
    """
    obj_processing_metadata = {'operation1': {'table': 'OutputLoadingUnloadingTimes',
                                              'columns':
                                                  {'duration': {'start': 'OperationBegins',
                                                                'stop': 'OperationFinish'},
                                                   'operation': 'OperationType',
                                                   'object_id': 'CubeName'}
                                              },
                               'operation2': {'table': 'OutputPalletProcessing',
                                              'columns':
                                                  {'duration': {'start': 'ProcessingStartTime',
                                                                'stop': 'ProcessingEndTime'},
                                                   'operation': 'RetortId',
                                                   'object_id': 'MaterialName'}
                                              }}

    table_obj_processing = pd.DataFrame()
    for o in obj_processing_metadata.keys():
        metadata = obj_processing_metadata[o]
        table_aux = tables.output_tables[metadata['table']]
        table_aux['duration'] = (table_aux[metadata['columns']['duration']['stop']] - table_aux[
            metadata['columns']['duration']['start']]).dt.total_seconds()
        table_aux = table_aux[['duration', metadata['columns']['operation'], metadata['columns']['object_id']]]
        table_aux.rename(
            columns={metadata['columns']['operation']: 'operation', metadata['columns']['object_id']: 'object_id'},
            inplace=True)
        table_obj_processing = table_obj_processing.append(table_aux, ignore_index=True)
    tables.output_tables['ObjectProcessingTable'] = table_obj_processing
    return tables


if __name__ == '__main__':
    path_output_tables = os.path.normpath(os.environ['PATHOUTPUTTABLES'])
    project_path = os.path.normpath(os.environ['PROJECTPATH'])
    project_name = os.environ['PROJECTNAME']
    model_name = os.environ['MODELNAME']

    simio_tables_ = SimioTables(path_to_project=project_path,
                                model_file_name=project_name,
                                model_name=model_name)
    simio_tables_.load_output_tables()
    print('Create Object Processing Table')
    output_tables_new_ = create_object_processing_table(simio_tables_)
    x_axis_ = 'object_id'
    y_axis_ = 'duration'
    operations_id = 'operation'
    simio_object_processing_plotter = SimioStackedBars(
        output_tables=output_tables_new_.output_tables,
        logger_level=logging.INFO,
        x_axis=x_axis_,
        y_axis=y_axis_,
        legend_col=operations_id)
    simio_object_processing_plotter.plot(tables='ObjectProcessingTable', kind='stacked_bars')
