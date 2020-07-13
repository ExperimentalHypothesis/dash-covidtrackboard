# module collecting utility functions/data (will be used in app layout, or in charts)

import requests, datetime, os
import pandas as pd
import numpy as np


def get_api_data(source: str):
    """ Get data from API source. """
    data = requests.get(source)
    return pd.read_json(data.text)


# get the global API data
daily_states_df = get_api_data("https://covidtracking.com/api/v1/states/daily.json")
daily_us_df = get_api_data("https://covidtracking.com/api/v1/us/daily.json")
current_state_df = get_api_data("https://covidtracking.com/api/v1/states/current.json")
current_us_df = get_api_data("https://covidtracking.com/api/v1/us/current.json")

# static data about state population
pop_df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "us-pop.json"))

# USA divisions
divisions = [{"New England": ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']},
    {"Mid-Atlantic": ['New Jersey', 'New York', 'Pennsylvania']},
    {"East North Central": ['Illinois', 'Indiana', 'Michigan', 'Ohio', 'Wisconsin']},
    {"West North Central": ["Iowa, Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota"]},
    {'South Atlantic': ('Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'District of Columbia', 'West Virginia')},
    {'East South Central': ('Alabama', 'Kentucky', 'Mississippi', 'Tennessee')},
    {'West South Central': ('Arkansas', 'Louisiana', 'Oklahoma', 'Texas')},
    {'Mountain': ('Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming')},
    {'Pacific': ('Alaska', 'California', 'Hawaii', 'Oregon', 'Washington')}]

# USA regions
regions = [
    {"Northeast":
        [
            {"New England": ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']},
            {"Mid-Atlantic": ['New Jersey', 'New York', 'Pennsylvania']}
        ]
     },

    {"Midwest":
        [
            {"East North Central": ['Illinois', 'Indiana', 'Michigan', 'Ohio', 'Wisconsin']},
            {"West North Central": ["Iowa, Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota"]},
        ]
     },

    {"South":
        [
            {'South Atlantic': ('Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'District of Columbia','West Virginia')},
            {'East South Central': ('Alabama', 'Kentucky', 'Mississippi', 'Tennessee')},
            {'West South Central': ('Arkansas', 'Louisiana', 'Oklahoma', 'Texas')},
        ]
     },

    {"West":
        [
            {'Mountain': ('Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming')},
            {'Pacific': ('Alaska', 'California', 'Hawaii', 'Oregon', 'Washington')}
        ]
    },
]


def create_df_for_date(date: str):
    """ Create dataframe for sunburts chart. It accepts date as a parsed string already, not as datetime.date object. """
    # slice the subdataframe and sum_up the numbers for particular date
    date_df = daily_states_df[daily_states_df["date"] == date]
    date_df["total positive"] = date_df["positive"].sum()
    date_df["total hospitalized"] = date_df["hospitalized"].sum()
    date_df["total recovered"] = date_df["recovered"].sum()
    date_df["total death"] = date_df["death"].sum()
    # merge it whole USA population
    date_df = pd.merge(date_df, pop_df)
    # add aditiononal cols and fill the cols with regions/divisions
    date_df["region"] = "None"
    date_df["division"] = "None"
    for region in regions:
        for region_name, region_list in region.items():
            for division in region_list:
                for division_name, states in division.items():
                    for state in states:
                        date_df.loc[(date_df["state name"] == state), "division"] = division_name
                        date_df.loc[(date_df["state name"] == state), "region"] = region_name

    # fix the possible zero div error
    cols = ["totalTestResults", "positive", "negative", "hospitalized", "recovered", "death"]
    date_df[cols] = date_df[cols].replace({0: np.nan})
    return date_df


def rename_datatable_columns() -> list:
    """ Rename datatable column names, since I dont want to rename dataframe columns globally. """
    df = current_state_df[["state", "totalTestResults", "positive", "hospitalized", "recovered", "death"]]
    cols = [{"name": i, "id": i, "deletable": False, "selectable": False} for i in df.columns]
    cols[0]["name"] = "State"
    cols[1]["name"] = "Tested"
    cols[2]["name"] = "Positive"
    cols[3]["name"] = "Hospitalized"
    cols[4]["name"] = "Recovered"
    cols[5]["name"] = "Fatal"
    return cols


def set_starting_date():
    """ Set the default staring date in date-picker for Map, Pie, Corelation and Sunburst chart. """
    today = datetime.date.today()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    return yesterday


if __name__ == "__main__":
    rename_datatable_columns()
