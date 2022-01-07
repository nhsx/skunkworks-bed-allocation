# Data Prepartion
---
This directory includes the file `create_json_files.py`.

This contains two functions (more information on these functions can be seen below):
- `create_hourly_elective_prob.json`
- `create_specialty_info_json`

To create the required json files for the forecast model respectfully:
- `hourly_elective_prob.json`
- `specialty_info.json`

It is important these files are generated from `patient_df.csv` for the forecast to be generated. It is important that `patient_df.csv` follows this data dictionary including all required fields and field formats. This can be found [here](../../config/patient_data_dictionary.json).

These functions can be called in a `.py` file or run in a notebook. An example of importing and running the functions can be seen below:
```
from data_preparation.create_json_files import (
    create_hourly_elective_prob.json,
    create_specialty_info_json,
)

create_hourly_elective_prob.json(
    "path/to/patient_df.csv", "directory_name"
)

create_specialty_info_json(
    "path/to/patient_df.csv", "path_to_is_medical_json", "directory_name"
)
```

## create_hourly_elective_prob.json
---
This function uses data from `patient_df.csv` to create `hourly_elective_prob.json`. This is needed
to create the forecast. It is important that `patient_df.csv` follows this data dictionary including
all required fields and field formats: `../../config/patient_data_dictionary.json`.

`hourly_elective_prob.json` represents the proportion of elective patients seen on that date and hour.

For example if 10 patients in total were seen on 21st July 1955 at 1pm, 4 were elective and 6 were non-elective the function would return 0.4 for that date and time (4/10).

time|elective patients|non-elective patient|total patient|portion of elective patients
---|---|---|---|---
21/07/1955 01:00:00|4|6|10|0.4
21/07/1955 02:00:00|5|20|25|0.2

```
Parameters
----------
    path_to_patient_df_csv : str
        The input is the path to the "patient_df.csv" file. With format: "../../config/patient_data_dictionary.json".

    output_directory: str
        The directory where "create_hourly_elective_prob.json" will be saved. The default is to be saved in the same directory as this file.

Returns
----------
    df : pd.DataFrame
        The dataframe aggregates the data from path_to_patient_df_csv and summarises the proportion of elective
        patients per date and hour.

    json file:
        Called - "create_hourly_elective_prob.json". This file is required to run the forecast and contains the df as summarised above.
        The file is saved in the directory define as the input.
```



## create_specialty_info_json
---
This function uses data from `patient_df.csv` to create `specialty_info.json`. This is needed to create the forecast. It is important that `patient_df.csv` follows this data dictionary including all required fields and field formats: `../../config/patient_data_dictionary.json`.

This function calculates the portion of patients seen in each speacility across the historic data found in `patient_df.csv` and maps the speciality to `is_medical` or not (more information on this below).

For example if there were three specialities that saw 20 patients in total, (real examples may include Urology or Cardiology but in this example spec1, spec2 and spec3 will be used) such as:

spec|number of patients (time period covers whole dataset)|proportion of patient seen by each speciality
---|---|---|
spec1| 5| 0.25
spec2| 10| 0.5
spec3| 5| 0.25
TOTAL| 20| 1

### **Creating required file is_medical_mapping json**
In order to run the function a **is_medical_json** file is required. This will contain a list of specilaities listed in `ADMIT_SPEC` in the `patient_df.csv` file and state whether it is medical or not by `true` or `false` in a [python dictionary format](https://docs.python.org/3/tutorial/datastructures.html). E.g. {"Urology" : false, "Cardiology": True}

An example of the file which needs to be created can be found [here](../../config/fake_data_categories/fake_speciality_is_medical_mapping.json). More information on json files and how to write and create json files can be found [here](https://www.w3schools.com/js/js_json_intro.asp)

Note:
- It is important that all categories listed in `ADMIT_SPEC` are included in your **is_medical_json** file.
- It is important that the same category names are used exactly, including capital letters and spaces.
- The file must be a json file and end in `.json`
- The file can be saved in any directory as long as your refer it correctly in the filepath

```
    Parameters
    ----------
    path_to_patient_df_csv : str
        The input is the path to the "patient_df.csv" file. With format: "../../config/patient_data_dictionary.json"

    path_to_is_medical_json: str
        This json file maps the categories "ADMIT_SPEC" to whether it is "is_medical" or not with "true" and "false".
        An example file to create can be found here: "../../config/fake_data_categories/fake_speciality_is_medical_mapping.json"
    
    output_directory: str
        The directory where "hourly_elective_prob.json" will be saved. The default is to be saved in the same directory as this file.

    Returns
    ----------
    df : pd.DataFrame
        The dataframe aggregates the data from path_to_patient_df_csv and summarises the proportion of elective patients per date and hour.

    json file:
        Called - "specialty_info.json". This file is required to run the forecast and contains the df as summarised above. The file is saved in the directory define as the input.
```