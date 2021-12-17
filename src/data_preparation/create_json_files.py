import pandas as pd
import json


def create_hourly_elective_prob_json(
    path_to_patient_df_csv: str, output_directory: str = "."
) -> pd.DataFrame:
    """
    This function uses data from "patient_df.csv" to create "hourly_elective_prob.json". This is needed
    to create the forecast. It is important that "patient_df.csv" follows this data dictionary including
    all required fields and field formats: "../../config/patient_data_dictionary.json".

    Parameters
    ----------
    path_to_patient_df_csv : str
        The input is the path to the ""patient_df.csv"" file. With format: "../../config/patient_data_dictionary.json"

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

    """

    # read in path to pandas dataframe.
    df_csv = pd.read_csv(path_to_patient_df_csv)

    # Group by "ADMIT_HOUR" and "ELECTIVE" and count number of patient in those categories.
    df = (
        df_csv.groupby(["ADMIT_HOUR", "ELECTIVE"])["DIM_PATIENT_ID"]
        .count()
        .reset_index()
    )

    # Group by "ADMIT_HOUR" and "ELECTIVE" and count number of patient in those categories.
    df = df.pivot(
        index="ADMIT_HOUR", columns="ELECTIVE", values="DIM_PATIENT_ID"
    )

    # Check there are only two categories in field "ELECTIVE" if not throw an error
    assert (
        len(df.columns) == 2
    ), f"ELECTIVE field must only contain 1 and 0. Current df columns: {df.columns}"

    # Add together the non elective and elective patient groupped by admit_hour
    try:
        df["sum"] = df[0] + df[1]

    # Throw value error if the columns 0 and 1 are not found
    except KeyError as e:
        raise ValueError("Elective field must only contain 1 and 0.") from e

    # For each hour state the proportion of elective patients per hour
    df["elective_prob"] = df[1] / df["sum"]

    # Round to two decimal places and fill in missing values
    df["elective_prob"] = df["elective_prob"].round(2).fillna(0)

    # Write dataframe to json format
    df["elective_prob"].to_json(
        f"{output_directory}/hourly_elective_prob.json"
    )

    # Message to show script has run
    print(
        f"Fake Data Generated! File saved: {output_directory}/hourly_elective_prob.json."
    )
    return df


def create_specialty_info_json(
    path_to_patient_df_csv: str,
    path_to_is_medical_json: str,
    output_directory: str = ".",
) -> pd.DataFrame:
    """
    This function uses data from "patient_df.csv" to create "specialty_info.json". This is needed
    to create the forecast. It is important that "patient_df.csv" follows this data dictionary including
    all required fields and field formats: "../../config/patient_data_dictionary.json".

    Parameters
    ----------
    path_to_patient_df_csv : str
        The input is the path to the "patient_df.csv" file. With format: "../../config/patient_data_dictionary.json"

    path_to_is_medical_json: str
        This json file maps the categories "ADMIT_SPEC" to whether it is "is_medical" or not with "true" and "false".
        An example file to create can be found here: "../../config/fake_data_categories/fake_speciality_is_medical_mapping.json"

    output_directory: str
        The directory where "specialty_info.json" will be saved. The default is to be saved in the same directory as this file.

    Returns
    ----------
    df : pd.DataFrame
        The dataframe aggregates the data from path_to_patient_df_csv and summarises the proportion of elective
        patients per date and hour.

    json file:
        Called - "specialty_info.json". This file is required to run the forecast and contains the df as summarised above.
        The file is saved in the directory define as the input.

    """

    # read in path to pandas dataframe.
    df_csv = pd.read_csv(path_to_patient_df_csv)

    # Group by admission speciality and count number of patients
    # reset index
    df = df_csv.groupby(["ADMIT_SPEC"])["DIM_PATIENT_ID"].count().reset_index()

    # Define the portion patients of that speiciality by taking the total patients
    # and dividing by the total for that specilaity
    df["probability"] = df["DIM_PATIENT_ID"] / sum(df["DIM_PATIENT_ID"])

    # Round to two decimal places and fill in missing values
    df["probability"] = df["probability"].round(2).fillna(0)

    # define if the department is medical or not
    # Load data_description.json to get columns required for training data
    mapping = load_is_medical_mapping(path_to_is_medical_json)

    # Add mappings to dataframe
    df = df.merge(mapping, on="ADMIT_SPEC")

    # Format for json"
    df.set_index("ADMIT_SPEC", drop=True, inplace=True)
    df_dict = df[["probability", "is_medical"]].transpose().to_dict()

    # Save to json file
    with open(f"{output_directory}/specialty_info.json", "w") as outfile:
        json.dump(df_dict, outfile)

    # Message to show script has run
    print(
        f"Fake Data Generated! File saved: {output_directory}/specialty_info.json."
    )

    return df


def load_is_medical_mapping(path_to_is_medical_json: str) -> pd.DataFrame:
    """
    This function takes the defined json value

    Parameters
    ----------
     path_to_is_medical_json: str
        This will contain a list of specilaities listed in `ADMIT_SPEC` in the `patient_df.csv` file and state whether
        it is medical or not by `true` or `false` in a python dictionary format, e.g. {"Urology" : false, "Cardiology": True}.
        An example of the file which needs to be created can be found here: "../../config/fake_data_categories/fake_speciality_is_medical_mapping.json".


    Returns
    ----------
    mapping_df : pd.DataFrame
        The dataframe contains the contents from the json file.

    """
    # Load json file
    with open(path_to_is_medical_json, "r") as file:
        mapping = json.load(file)

    # Read contents and fornat
    mapping_df = pd.DataFrame.from_dict(mapping, orient="index")
    mapping_df.reset_index(level=0, inplace=True)

    # Rename columns in dataframe
    mapping_df.rename(
        {"index": "ADMIT_SPEC", 0: "is_medical"}, axis=1, inplace=True
    )

    return mapping_df
