import os
import logging
from simio_lisa.simio_plots import SimioTimeSeries, SimioBarPie, SimioBox, SimioStackedBars
from simio_lisa.simio_tables import SimioTables


def import_output_tables():
    env_project_path = os.environ['SIMIOPROJECTPATH']
    env_project_file = os.environ['SIMIOPROJECTNAME']
    env_model_name = os.environ['MODELNAME']
    output_tables = SimioTables(path_to_project=env_project_path,
                                model_file_name=env_project_file,
                                model_name=env_model_name)
    output_tables.load_output_tables()
    return output_tables

def import_input_tables():
    env_project_path = os.environ['SIMIOPROJECTPATH']
    env_project_file = os.environ['SIMIOPROJECTNAME']
    env_model_name = os.environ['MODELNAME']
    input_tables = SimioTables(path_to_project=env_project_path,
                                model_file_name=env_project_file,
                                model_name=env_model_name)
    input_tables.load_input_tables()
    return input_tables

def test_smoke_time_series():
    output_tables = import_output_tables()
    y_axis = 'Utilization'
    time_axis = 'DateTime'
    simio_time_series_plotter = SimioTimeSeries(
                      output_tables=output_tables.output_tables,
                      logger_level=logging.INFO,
                      y_axis=y_axis,
                      time_axis=time_axis)

    simio_time_series_plotter.plot(tables='OutputObjectUtilization', kind='time_series_columns')
    simio_time_series_plotter.time_axis = 'StatusDate'
    simio_time_series_plotter.y_axis = 'Count'
    simio_time_series_plotter.plot(tables=['OutputStatus5A', 'OutputStatus5B', 'OutputStatus6'],
                                   kind='time_series_tables')
    assert True


def test_smoke_bar_and_pie_charts():
    output_tables = import_output_tables()
    x_axis = 'ObjectId'
    y_axis = 'Utilization'
    time_axis = 'DateTime'
    object_groups_dict = {'Shuttles': ['DropOffShuttle[1]', 'PickUpShuttle[1]'],
                          'Retorts': ['Retort1', 'Retort2', 'Retort3', 'Retort4',
                                      'Retort5', 'Retort6', 'Retort7', 'Retort8',
                                      'Retort9', 'Retort10']
                          }
    simio_obj_util_plotter = SimioBarPie(
        output_tables=output_tables.output_tables,
        logger_level=logging.INFO,
        x_axis=x_axis,
        y_axis=y_axis,
        time_axis=time_axis,
        objects_dict=object_groups_dict)
    simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='bars_plot')
    simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='pie_plot')
    simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='bars_time_series_plot')
    assert True


def test_smoke_box_plot():
    output_tables = import_output_tables()
    x_axis = 'ProcessName'
    y_axis = 'ProductTimeInSystem'
    simio_tis_plotter = SimioBox(
        output_tables=output_tables.output_tables,
        logger_level=logging.INFO,
        y_axis=y_axis,
        x_axis=x_axis)

    simio_tis_plotter.plot(tables='OutputProductDeparture', kind='box_plot')
    assert True


def _test_smoke_stack_bar():
    output_tables = import_output_tables()
    x_axis = 'ObjectID'
    y_axis = 'Duration'
    legend_col = 'OperationID'
    simio_object_processing_plotter = SimioStackedBars(
        output_tables=output_tables.output_tables,
        logger_level=logging.INFO,
        x_axis=x_axis,
        y_axis=y_axis,
        legend_col=legend_col)
    simio_object_processing_plotter.plot(tables='ObjectProcessingTable', kind='stacked_bars')
    assert True
