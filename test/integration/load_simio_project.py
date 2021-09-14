import os
from simio_lisa.load_simio_project import load_output_tables


if __name__ == '__main__':
    env_project_path = os.environ['SIMIOPROJECTPATH']
    env_project_file = os.environ['SIMIOPROJECTNAME']
    env_model_name = os.environ['MODELNAME']
    env_export_dir = os.environ['EXPORTDIR']
    os.mkdir(env_export_dir)
    output_tables = load_output_tables(project_path=env_project_path,
                                       project_filename=env_project_file,
                                       model_name=env_model_name)
    for table_name, table_df in output_tables.items():
        print(os.path.join(env_export_dir, f'{table_name}.csv'))
        try:
            table_df.to_csv(os.path.join(env_export_dir, f'{table_name}.csv'), index=False)
        except AttributeError:
            print("This was empty")
