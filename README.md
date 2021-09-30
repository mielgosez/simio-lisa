# simio-lisa
Python package of processing tools for Simio models saved as .simproj

# How to install it
This package has been published in pypi and in order to install it you have

```
pip install simio-lisa
```

# How to use it

## Exporting Input and Output Tables

```
import os
from simio_lisa.load_simio_project import load_output_tables, load_input_tables


if __name__ == '__main__':
    env_project_path = "path to project"
    env_project_file = "name of .simproj file"
    env_model_name = "name of the model containing the output file (usually Model)"
    env_export_dir = "directory where output tables are going to be saved"
    os.mkdir(env_export_dir)
    tables_ = SimioTables(path_to_project=env_project_path,
                          model_file_name=env_project_file,
                          model_name=env_model_name)
    tables_.load_output_tables()
    tables_.load_input_tables()
    
    # only for the output tables, saved as the attribute output_tables:
    for table_name, table_df in tables_.output_tables.items():
        print(os.path.join(env_export_dir, f'{table_name}.csv'))
        try:
            for col_name, col_type in table_df.dtypes.items():
                if col_type.name == 'datetime64[ns]':
                    table_df[col_name] = table_df[col_name].dt.strftime('%d-%m-%Y %X')
            table_df.to_csv(os.path.join(env_export_dir, f'{table_name}.csv'), index=False, decimal='.')
        except AttributeError:
            print("This was empty")
```

## Exporting Experiments

```
import os
from simio_lisa.load_simio_project import load_experiment_results


if __name__ == '__main__':
    env_project_path = "path to project"
    env_project_file = "name of .simproj file"
    env_model_name = "name of the model containing the output file (usually Model)"
    experiments_df = load_experiment_results(project_path=env_project_path,
                                             project_filename=env_project_file,
                                             model_name=env_model_name,
                                             agg_function=np.mean)
```

## Plotting Data from tables
Different classes are defined for different kinds of plot. Their parent class is SimioPlotter, and it wants as an input a dictionary with all the tables (e.g. the attribute tables of an object of the class SimioTables).
Other possible inputs can be x_axis, y_axis, time_axis, legend_col, object_groups_dict.
Each child class must cointain a plot() method.
The child classes are: SimioTimeSeries (plot time series), SimioBarPie (bar plots and pie charts), SimioBox (box plot), SimioStackedBars (stacked bars plot).

Examples for the
### Initialize SimioTables class object
We initialize it as output_tables. Actually it contains both output tables and input tables but in the example we are going to use only the output ones.

    output_tables = SimioTables(path_to_project,
                                 model_file_name,
                                 model_name)
    output_tables.load_output_tables()

### Plot time series comparing different columns of the same table

    y_axis = 'Utilization'
    time_axis = 'DateTime'
    simio_time_series_plotter = SimioTimeSeries(
                      output_tables=output_tables.output_tables,
                      logger_level = logging.INFO,
                      y_axis= y_axis,
                      time_axis=time_axis)

    simio_time_series_plotter.plot(tables='OutputObjectUtilization', kind='time_series_columns')

### Plot time series comparing same column from different tables (name of tables as legend)

    y_axis = 'Count'
    time_axis = 'StatusDate'
    simio_time_series_plotter = SimioTimeSeries(
                      output_tables=output_tables.output_tables,
                      logger_level = logging.INFO,
                      y_axis= y_axis,
                      time_axis=time_axis)

    simio_time_series_plotter.plot(tables=['OutputStatus5A', 'OutputStatus5B', 'OutputStatus6'], kind='time_series_tables')

### Plot bars or pie charts, distinguishing plots via object_groups_dict dictionary

    x_axis = 'ObjectId'
    y_axis = 'Utilization'
    object_groups_dict = {'Shuttles': ['DropOffShuttle[1]', 'PickUpShuttle[1]'],
                          'Retorts': ['Retort1', 'Retort2', 'Retort3', 'Retort4',
                                      'Retort5', 'Retort6', 'Retort7', 'Retort8',
                                      'Retort9', 'Retort10']
                          }
    simio_obj_util_plotter = SimioBarPie(
                      output_tables=output_tables.output_tables,
                      logger_level = logging.INFO,
                      x_axis = x_axis,
                      y_axis = y_axis,
                      objects_dict = object_groups_dict)

    simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='bars_plot')
    simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='pie_plot')

### Plot bars along time, distinguishing plots via object_groups_dict dictionary (each key should contain all the objects to be compared together)

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
                      logger_level = logging.INFO,
                      x_axis = x_axis,
                      y_axis = y_axis,
                      time_axis = time_axis,
                      objects_dict = object_groups_dict)

    simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='bars_time_series_plot')

### Box plot

    x_axis = 'ProcessName'
    y_axis = 'ProductTimeInSystem'
    simio_tis_plotter = SimioBox(
        output_tables=output_tables.output_tables,
        logger_level=logging.INFO,
        y_axis=y_axis,
        x_axis=x_axis)

    simio_tis_plotter.plot(tables='OutputProductDeparture', kind='box_plot')

### Plot stacked bars, using as a legend the column legend_col

    x_axis = 'ObjectID'
    y_axis = 'Duration'
    legend_col = 'OperationID'
    simio_object_processing_plotter = SimioStackedBars(
                      output_tables=output_tables.output_tables,
                      logger_level = logging.INFO,
                      x_axis = x_axis,
                      y_axis = y_axis,
                      legend_col = legend_col)
    simio_object_processing_plotter.plot(tables='ObjectProcessingTable', kind='stacked_bars')