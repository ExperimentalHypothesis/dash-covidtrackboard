# module collecting utility functions (eg. functions that will be used in app layout, or somewhere near)


def get_api_data(source:str):
    ''' Get data from API source '''

    data = requests.get(source)
    return pd.read_json(data.text)


def rename_datatable_columns():
    """ Rename datatable columns. I am doing it this way since i dont want to rename dataframe colums directly """

    cols = [{"name": i, "id": i, "deletable": False, "selectable": False} for i in grouped_df.columns]
    cols[0]["name"] = "State"
    cols[1]["name"] = "Tested"
    cols[2]["name"] = "Positive"
    cols[3]["name"] = "Hospitalized"
    cols[4]["name"] = "Recovered"
    cols[5]["name"] = "Fatal"
    return cols


def set_starting_date():
    """ Set a defaalt staring date in date-picker for map, pie, corelation and sunburst chart """

    today = datetime.date.today()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    return yesterday