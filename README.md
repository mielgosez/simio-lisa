# simio-lisa
Python package of processing tools for Simio models saved as .simproj

# How to install it
This package has been published in pypi and in order to install it you have

```
pip install simio-lisa
```

# How to use it

## Exporting Output Tables

```
import os
from simio_lisa.load_simio_project import load_output_tables


if __name__ == '__main__':
    env_project_path = "path to project"
    env_project_file = "name of .simproj file"
    env_model_name = "name of the model containing the output file (usually Model)"
    env_export_dir = "directory where output tables are going to be saved"
    output_tables = load_output_tables(project_path=env_project_path,
                                       project_filename=env_project_file,
                                       model_name=env_model_name)
    for table_name, table_df in output_tables.items():
        print(os.path.join(env_export_dir, f'{table_name}.csv'))
        try:
            table_df.to_csv(os.path.join(env_export_dir, f'{table_name}.csv'), index=False)
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