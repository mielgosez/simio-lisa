import os
from simio_lisa.output_tables import OutputTables


if __name__ == '__main__':
    env_project_path = os.environ['SIMIOPROJECTPATH']
    env_project_file = os.environ['SIMIOPROJECTNAME']
    env_model_name = os.environ['MODELNAME']
    env_export_dir = os.environ['EXPORTDIR']
    # os.mkdir(env_export_dir)
    output_tables = OutputTables(path_to_project=env_project_path,
                                 model_file_name=env_project_file,
                                 model_name=env_model_name)
    output_tables.load_output_tables()
    for table_name, table_df in output_tables.tables.items():
        print(os.path.join(env_export_dir, f'{table_name}.csv'))
        try:
            for col_name, col_type in table_df.dtypes.items():
                if col_type.name == 'datetime64[ns]':
                    table_df[col_name] = table_df[col_name].dt.strftime('%d-%m-%Y %X')
            table_df.to_csv(os.path.join(env_export_dir, f'{table_name}.csv'), index=False, decimal='.')
        except AttributeError:
            print("This was empty")
