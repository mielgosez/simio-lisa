import pandas as pd
import datapane as dp
import os
from output_tables import OutputTables
from simio_plots import SimioTimeSeries, SimioBarPie
import logging

path_output_tables = os.path.normpath(os.environ['PATHOUTPUTTABLES'])
project_path = os.path.normpath(os.environ['PROJECTPATH'])
project_name = os.environ['PROJECTNAME']
model_name = os.environ['MODELNAME']

output_tables = OutputTables(path_to_project=project_path,
                             model_file_name=project_name,
                             model_name=model_name)
output_tables.load_output_tables()

print('Time Series plots')
y_axis = 'Count'
time_axis = 'StatusDate'
simio_time_series_plotter = SimioTimeSeries(
    output_tables=output_tables.tables,
    logger_level=logging.INFO,
    y_axis=y_axis,
    time_axis=time_axis)
fig1 = simio_time_series_plotter.plot(tables=['OutputStatus5A', 'OutputStatus5B', 'OutputStatus6'], kind='time_series_tables')
#
print('Object Utilization plots')
x_axis = 'ObjectId'
y_axis = 'Utilization'
time_axis = 'DateTime'
object_groups_dict = {'Shuttles': ['DropOffShuttle[1]', 'PickUpShuttle[1]'],
                      'Retorts': ['Retort1', 'Retort2', 'Retort3', 'Retort4',
                                  'Retort5', 'Retort6', 'Retort7', 'Retort8',
                                  'Retort9', 'Retort10']
                      }
simio_obj_util_plotter = SimioBarPie(
    output_tables=output_tables.tables,
    logger_level=logging.INFO,
    x_axis=x_axis,
    y_axis=y_axis,
    time_axis=time_axis,
    objects_dict=object_groups_dict)

fig2 = simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='bars_plot')
fig3 = simio_obj_util_plotter.plot(tables='OutputObjectUtilization', kind='pie_plot')




# embed into a Datapane Report
report1 = dp.Report(
    "## Test Report",
    dp.Plot(fig1, caption='figure1'),
    dp.Select(blocks=[
        dp.Plot(fig2['Shuttles'], label='Shuttles'),
        dp.Plot(fig2['Retorts'], label='Retorts')
                    ]),
    dp.Group(
        dp.Plot(fig2['Shuttles'], caption='Shuttles'),
        dp.Plot(fig2['Retorts'],  caption='Retorts'),
        columns=2
            ),
    dp.DataTable(output_tables.tables['OutputLoadingUnloadingTimes'], caption="Output Loading and Unloading Times Table"),
    dp.DataTable(output_tables.tables['OutputFailures'], caption="COutput Failures Table"))
report1.save("report1.html", open=True)

report2 = dp.Report(
    "## Test Report",
    dp.Plot(fig1, caption='figure1'),
    dp.Select(blocks=
            [dp.Plot(fig2[ii], label=ii) for ii in fig2.keys()]
                    ),
    dp.Group(blocks=
            [dp.Plot(fig3[ii], caption=ii) for ii in fig3.keys()], columns=len(fig3.keys())
                    ),
    dp.DataTable(output_tables.tables['OutputLoadingUnloadingTimes'], caption="Output Loading and Unloading Times Table"),
    dp.DataTable(output_tables.tables['OutputFailures'], caption="Output Failures Table"))
report2.save("report2.html", open=True)

metadata = {
    'block1': {'obj': fig1,
               'caption': 'figure1',
               'kind': 'plot'},
    'block2': {'obj': fig2,
               'kind': 'plot',
               'grouping': 'select'},
    'block3': {'obj': [output_tables.tables['OutputLoadingUnloadingTimes'],
                       output_tables.tables['OutputFailures']],
               'caption': ["Output Loading and Unloading Times Table",
                           "Output Failures Table"],
               'columns': 2,
               'kind': ['table', 'table']}
}

report3 = dp.Report(
    "## Test Report",
    dp.Group(blocks=
             [dp.Plot(metadata[m]['obj']) for m in metadata.keys()[:2]]
             ),
    dp.Plot(fig1, caption='figure1'),
    dp.Select(blocks=
            [dp.Plot(fig2[ii], label=ii) for ii in fig2.keys()]
                    ),
    dp.Group(blocks=
            [dp.Plot(fig3[ii], caption=ii) for ii in fig3.keys()], columns=len(fig3.keys())
                    ),
    dp.DataTable(output_tables.tables['OutputLoadingUnloadingTimes'], caption="Output Loading and Unloading Times Table"),
    dp.DataTable(output_tables.tables['OutputFailures'], caption="Output Failures Table"))
report3.save("report3.html", open=True)

report3 = dp.Report(
    "## Test Report",
    dp.Group(blocks=
             [dp.Plot(metadata[m]['obj']) for m in metadata.keys()]
             ),
    dp.Plot(fig1, caption='figure1'),
    dp.Select(blocks=
            [dp.Plot(fig2[ii], label=ii) for ii in fig2.keys()]
                    ),
    dp.Group(blocks=
            [dp.Plot(fig3[ii], caption=ii) for ii in fig3.keys()], columns=len(fig3.keys())
                    ),
    dp.DataTable(output_tables.tables['OutputLoadingUnloadingTimes'], caption="Output Loading and Unloading Times Table"),
    dp.DataTable(output_tables.tables['OutputFailures'], caption="Output Failures Table"))
report3.save("report3.html", open=True)

# To make a figure
df = output_tables.tables['OutputLoadingUnloadingTimes']
fig = go.Figure(data=[go.Table(
    header=dict(values=list(df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=df.transpose().values.tolist(),
               fill_color='lavender',
               align='left'))
])