# module collecting utility functions/data (ewill be used in app layout, or in charts)

import requests, datetime, os
import pandas as pd


def get_api_data(source:str):
    ''' Get data from API source '''

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
divisions = [{"New England" : ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']},
    {"Mid-Atlantic": ['New Jersey', 'New York', 'Pennsylvania']},
    {"East North Central": ['Illinois', 'Indiana', 'Michigan', 'Ohio','Wisconsin']},
    {"West North Central": ["Iowa, Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota"]},
    {'South Atlantic': ('Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'District of Columbia','West Virginia')},
    {'East South Central': ('Alabama', 'Kentucky', 'Mississippi', 'Tennessee')},
    {'West South Central': ('Arkansas', 'Louisiana', 'Oklahoma', 'Texas')},
    {'Mountain': ('Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming')},
    {'Pacific': ('Alaska', 'California', 'Hawaii', 'Oregon', 'Washington')}]
 
# USA regions
regions= [
    { "Northeast":
        [
            {"New England" : ['Connecticut', 'Maine', 'Massachusetts', 'New Hampshire', 'Rhode Island', 'Vermont']},
            {"Mid-Atlantic": ['New Jersey', 'New York', 'Pennsylvania']}
        ]
    },
    { 
        "Midwest":
        [
            {"East North Central": ['Illinois', 'Indiana', 'Michigan', 'Ohio','Wisconsin']},
            {"West North Central": ["Iowa, Kansas", "Minnesota", "Missouri", "Nebraska", "North Dakota", "South Dakota"]},
        ]
    },
    {
        "South":
        [
            {'South Atlantic': ('Delaware', 'Florida', 'Georgia', 'Maryland', 'North Carolina', 'South Carolina', 'Virginia', 'District of Columbia','West                  Virginia')},
            {'East South Central': ('Alabama', 'Kentucky', 'Mississippi', 'Tennessee')},
            {'West South Central': ('Arkansas', 'Louisiana', 'Oklahoma', 'Texas')},
        ]
    },
    {
        "West":
        [
            {'Mountain': ('Arizona', 'Colorado', 'Idaho', 'Montana', 'Nevada', 'New Mexico', 'Utah', 'Wyoming')},
            {'Pacific': ('Alaska', 'California', 'Hawaii', 'Oregon', 'Washington')}
        ]
    },
]




def rename_datatable_columns() -> list:
    """ Rename datatable column names, since I dont want to rename dataframe columns globally """

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
    """ Set the default staring date in date-picker for Map, Pie, Corelation and Sunburst chart """

    today = datetime.date.today()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    return yesterday



if __name__ == "__main__":
    rename_datatable_columns()
