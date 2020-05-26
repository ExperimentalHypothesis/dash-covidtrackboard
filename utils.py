# module collecting utility functions (eg. functions that will be used in app layout, or somewhere near, but cant be defined in there)

import requests, datetime, os
import pandas as pd




def get_api_data(source:str):
    ''' Get data from API source '''

    data = requests.get(source)
    return pd.read_json(data.text)

# TODO finish. maybe no need to renaming, just rename the datatable cols in the copy

def rename_datatable_columns():
    """ Rename datatable columns. I am doing it this way since I dont want to rename dataframe colums directly """

    # daily_states_df = get_api_data("https://covidtracking.com/api/v1/states/daily.json")
    # pop_df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "us-pop.json"))

    # df = pd.merge(daily_states_df, pop_df, on="state")
    # grouped_df = df.groupby("state", as_index=False)[["totalTestResults", "positive", "hospitalized", "recovered", "death"]].sum()

    current_state_df = get_api_data("https://covidtracking.com/api/v1/states/current.json")
    grouped_df = current_state_df.groupby("state", as_index=False)[["totalTestResults", "positive", "hospitalized", "recovered", "death"]].sum()


    cols = [{"name": i, "id": i, "deletable": False, "selectable": False} for i in grouped_df.columns]
    cols[0]["name"] = "State"
    cols[1]["name"] = "Tested"
    cols[2]["name"] = "Positive"
    cols[3]["name"] = "Hospitalized"
    cols[4]["name"] = "Recovered"
    cols[5]["name"] = "Fatal"
    return cols


def set_starting_date():
    """ Set a default staring date in date-picker for Map, Pie, Corelation and Sunburst chart """

    today = datetime.date.today()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    return yesterday