import requests, os
import pandas as pd
import numpy as np
import heapq

# plotly imports
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def get_api_data(source: str):
    """ Get data from api, return dateframe. """
    data = requests.get(source)
    return pd.read_json(data.text)


# get the global data - there will be a local copy in each function
daily_states_df = get_api_data("https://covidtracking.com/api/v1/states/daily.json")
daily_us_df = get_api_data("https://covidtracking.com/api/v1/us/daily.json")
current_state_df = get_api_data("https://covidtracking.com/api/v1/states/current.json")
current_us_df = get_api_data("https://covidtracking.com/api/v1/us/current.json")


pop_df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "us-pop.json"))

def cumulative_linechart_us():
    """ Create linechart showing the cummulative progression in time. """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["totalTestResults"], mode='lines', name='Tested'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["negative"], mode='lines', name='Negative'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["positive"], mode='lines', name='Positive'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["hospitalized"], mode='lines', name='Hospitalized'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["recovered"], mode='lines', name='Recovered'))
    fig.add_trace(go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["death"], mode='lines', name='Fatal'))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', title="Progression in Time")

    fig.update_layout(
        legend=dict(
            x=0.01,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
    )
    return fig


def cumulative_barchart_us():
    """ Create barchart for USA cumulative data. """
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["Positive"], y=current_us_df["positive"], name='Positive'))
    fig.add_trace(go.Bar(x=["Hospitalized"], y=current_us_df["hospitalizedCumulative"], name='Hospitalized'))
    fig.add_trace(go.Bar(x=["Pending"], y=current_us_df["pending"], name='Pending'))
    fig.add_trace(go.Bar(x=["Fatal"], y=current_us_df["death"], name='Fatal'))
    fig.update_layout(title_text='Cumulative Barmode', plot_bgcolor='rgba(0,0,0,0)')
    return fig


def total_tests_pie():
    """ Create piechart for total test. """
    fig = px.pie(current_us_df,
                 values=[current_us_df["positive"][0], current_us_df["negative"][0], current_us_df["pending"][0]], 
                 names=['Positive', 'Negative', 'Pending'],
                 title='Tests Total')
    fig.update_layout(legend_orientation="h", margin=dict(l=20, r=20))
    return fig


def hosp_death_daily_increase():
    """ Create line chart for daily increase. """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["deathIncrease"], name="Fatal Cases", mode='lines'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=daily_us_df["dateChecked"].str.split("T").str[0], y=daily_us_df["positiveIncrease"], name="Positive Cases", mode='lines'),
        secondary_y=True,
    )
    fig.update_layout(
        title_text="Daily Increase of Positive & Fatal Cases",
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            x=0.01,
            y=1.0,
            # bgcolor='rgba(255, 255, 255, 0)',
            # bordercolor='rgba(255, 255, 255, 0)'
        ),
        margin=dict(l=20, r=20)
    )
    fig.update_yaxes(title_text="<b>Fatal</b> Daily Increase", secondary_y=False)
    fig.update_yaxes(title_text="<b>Positive</b> Daily Increase", secondary_y=True)
    return fig


def hospitalized():
    """ Create horizontal barchart for hospitalized cases. """
    fig = go.Figure(data=[
        go.Bar(name='Cumulative',
               orientation='h',
               y=["Hospitalized", "In ICU", "On Ventilator"],
               x=[current_us_df["hospitalizedCumulative"][0], current_us_df["inIcuCurrently"][0], current_us_df["onVentilatorCurrently"][0]],
               showlegend=False),

        go.Bar(name='Current',
               orientation='h',
               y=["Hospitalized", "In ICU", "On Ventilator"],
               x=[current_us_df["hospitalizedCurrently"][0], current_us_df["inIcuCumulative"][0], current_us_df["onVentilatorCumulative"][0]],
               showlegend=False)
    ])

    fig.update_layout(barmode='group', plot_bgcolor='rgba(0,0,0,0)', title='Hospitalization')
    return fig


def corelation_positive_population():
    """ Create scatter chart for corelation. """
    pop_df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "us-pop.json"))
    state_df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "state-current.json"))
    df = pd.merge(state_df, pop_df, on="state")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["pop"], y=df["positive"].fillna(0), mode='markers', text=df['state name'].fillna(0)))
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)',
                      title='Corelation between population and positive', 
                      autosize=False,
                      width=400,
                      height=600,
                      margin=dict(
                            l=10,
                            r=10,
                            # b=30,
                            # t=30,
                            # pad=4
                            ),)
    return fig


def scatter_bar_population_positive():
    """ Create barchart/scatter for us states using subplots. """
    pop_df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "us-pop.json"))
    df = pd.merge(current_state_df, pop_df, on="state")
    pint = [int(i.replace(",",""))for i in df["pop"]]

    y_positive_df = np.rint(df["positive"] / pint * 1_000_000)
    y_population_df = pint
    x_state_df = current_state_df["state"]

    fig = make_subplots(rows=2, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.02)

    fig.add_trace(go.Scatter(x=x_state_df,
                             y=y_positive_df,
                             name='Density of Reported Cases in the Population [for 1 Mil.]',
                             mode='lines+markers',
                             line_color="rgba(0,0,0,0.7)",
                             line_width=1),
                  row=2,
                  col=1)

    fig.add_trace(go.Bar(x=x_state_df,
                         y=y_population_df,
                         name='State Population [in Mil.]',
                         marker=dict(color="rgba(50,171,96,0.6)",
                                     line=dict(color="rgba(50,171,96,1)",
                                               width=1,
                                               )
                                     ),
                         ),
                  row=1,
                  col=1)

    fig.update_layout(height=600,
                      plot_bgcolor='rgba(0, 0, 0, 0)',
                      title_text="Population by State & Density of Reported Cases",
                      xaxis=dict(showgrid=False,
                                 showline=False,
                                 showticklabels=True,
                                 linecolor='rgba(102, 102, 102, 0.8)',
                                 linewidth=2,
                                 # domain=[0, 0.7],
                                 ),
                      xaxis2=dict(showgrid=True,
                                  showline=True,
                                  linecolor='rgba(102, 102, 102, 0.8)',
                                  linewidth=2,
                                  showticklabels=False,
                                  # domain=[0, .7],
                                  ),
                      yaxis=dict(zeroline=False,
                                 showline=False,
                                 showticklabels=True,
                                 showgrid=True,
                                 domain=[0, 0.42],
                                 ),
                      yaxis2=dict(zeroline=False,
                                  showline=False,
                                  showticklabels=True,
                                  showgrid=True,
                                  domain=[0.47, 1],
                                  side='top',
                                  dtick=100000,
                                  ),
                      legend=dict(x=0.029,
                                  y=1.038,
                                  font_size=10
                                  ),

                    # margin=dict(
                    #     l=100, 
                    #     r=20,
                    #     t=70, 
                    #     b=70
                    # ),
            )

    # anotations
    largest_positive = heapq.nlargest(5, y_positive_df)
    for xa, ya in zip(x_state_df, y_positive_df):
        if ya in largest_positive:
            fig.add_annotation(
                xref='x2',
                yref='y2',
                x=xa,
                y=ya + 1300,
                text="{:,}".format(ya),
                showarrow=False)

    return fig


def create_mortality_barchart():
    """ Create mortality barchart. """
    grouped_df = daily_states_df.groupby("state", as_index=False)[["totalTestResults", "positive", "hospitalized", "recovered", "death"]].sum()
    grouped_df["mortality"] = grouped_df["death"]/grouped_df["positive"] * 100
    fig = px.bar(grouped_df, y='mortality', x='state', text='mortality')
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')

    fig.update_layout(uniformtext_minsize=8, 
                      uniformtext_mode='hide',
                      height=350,
                      title='Mortality Rate by State',
                      # title={
                      #     'text': 'Mortality Rate by State',
                      #     'y':0.9,
                      #     'x':0.5,
                      #     # 'xanchor': 'center',
                      #     'yanchor': 'top'
                      #     },
                      plot_bgcolor='rgba(0,0,0,0)',
                      yaxis=dict(title='Mortality Rate in %',
                                 # titlefont_size=15,
                                 # tickfont_size=13
                                 ),
                      xaxis=dict(title='',),
                      margin=dict(t=50, l=0, r=0, b=50),
                    )
    return fig

def distribution_by_divisions():
    """ create sunburst chart for divisions, regions, states """

    df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "sunburst.json"))
    # print(df.head())
    # print(current_state_df.columns)
    # print(current_state_df.head())

    loc_current_state_df = current_state_df[["state", "totalTestResults", "positive", "negative", "hospitalized", "recovered", "death"]]
    loc_daily_states_df = daily_states_df[["dateChecked","state", "totalTestResults", "positive", "negative", "hospitalized", "recovered", "death"]]
    # print(loc_current_state_df.head())
    # print(loc_daily_states_df.head())
    # print(pop_df.head())

    mrg_current_states_df = pd.merge(loc_current_state_df, pop_df, on="state")
    mrg_daily_states_df = pd.merge(loc_daily_states_df, pop_df, on="state")
    # print(mrg_current_states_df)
    # print(mrg_daily_states_df)

    mrg_current_states_df["total positive usa"] = mrg_current_states_df["positive"].sum()
    mrg_current_states_df["total hospitalized usa"] = mrg_current_states_df["hospitalized"].sum()
    mrg_current_states_df["total recovered usa"] = mrg_current_states_df["recovered"].sum()
    mrg_current_states_df["total death usa"] = mrg_current_states_df["death"].sum()
    # print(mrg_current_states_df)

    mrg_daily_states_df["total positive usa"] = mrg_daily_states_df["positive"].sum()
    mrg_daily_states_df["total hospitalized usa"] = mrg_daily_states_df["hospitalized"].sum()
    mrg_daily_states_df["total recovered usa"] = mrg_daily_states_df["recovered"].sum()
    mrg_daily_states_df["total death usa"] = mrg_daily_states_df["death"].sum()


    mrg_current_states_df["region"] = "None"
    mrg_current_states_df["division"] = "None"
    # print(mrg_current_states_df)

    mrg_daily_states_df["region"] = "None"
    mrg_daily_states_df["division"] = "None"

    # fill the regions and divisions to dataframe
    for region in regions:
        for region_name, region_list in region.items():
            for division in region_list:
                for division_name, states in division.items():
                    for state in states:
                        mrg_daily_states_df.loc[(mrg_daily_states_df["state name"] == state),"division"]=division_name
                        mrg_daily_states_df.loc[(mrg_daily_states_df["state name"] == state),"region"]=region_name

    for region in regions:
        for region_name, region_list in region.items():
            for division in region_list:
                for division_name, states in division.items():
                    for state in states:
                        mrg_current_states_df.loc[(mrg_current_states_df["state name"] == state),"division"]=division_name
                        mrg_current_states_df.loc[(mrg_current_states_df["state name"] == state),"region"]=region_name


    cols = ["totalTestResults", "positive", "negative", "hospitalized", "recovered", "death"]
    mrg_current_states_df[cols] = mrg_current_states_df[cols].replace({0:np.nan})

    fig = px.sunburst(mrg_current_states_df,
                    path=["total positive usa", "region", "division", "state"], 
                    values='positive', 
                    color="death", 
                    color_continuous_scale="Rdbu",)
    fig.update_layout(
        height=600, 
        title="Positive Cases by Region - Click To Expand",
        margin=dict(
                    l=1,
                    r=1,
                    b=70,
                    t=100,
                )
        )
    return fig
