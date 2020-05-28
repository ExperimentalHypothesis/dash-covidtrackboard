import requests, json, os
import pandas as pd
import numpy as np
import datetime

# plotly imports
import plotly, json, requests   
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# dash imports
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash, dash_table
import dash_core_components as dcc 
import dash_html_components as html 
import dash_bootstrap_components as dbc

# custom imports
from utils import rename_datatable_columns, set_starting_date, get_api_data, regions, create_df_for_date
from charts import hosp_death_daily_increase, create_mortality_barchart, cumulative_linechart_us, total_tests_pie, hospitalized, corelation_positive_population, cumulative_barchart_us, scatter_bar_population_positive, distribution_by_divisions

# get the global API data 
daily_states_df = get_api_data("https://covidtracking.com/api/v1/states/daily.json")
daily_us_df = get_api_data("https://covidtracking.com/api/v1/us/daily.json")
current_state_df = get_api_data("https://covidtracking.com/api/v1/states/current.json")
current_us_df = get_api_data("https://covidtracking.com/api/v1/us/current.json")

# static data about state population - scrapped from wikipedia
pop_df = pd.read_json(os.path.join(os.path.dirname(__file__), "data", "us-pop.json"))


# merged df used for for all callback charts 
df = pd.merge(daily_states_df, pop_df, on="state")
# pd.set_option("display.max_columns", None)


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css", dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div([
    html.H1(children='COVID-19 US Data Tracker', style={"margin": "50px auto 0 auto", "margin-bottom": "50px"}),

    #-------------------------- FIRST SECTION: NUMBERS OF 4 CASES -------------------------------------

    html.Div([   
        html.Div([
            dbc.Jumbotron(           
            [
                html.H3(f"{daily_us_df['positive'][0]:,}", className="display-4"),
                html.P(
                    "Positive cases",
                    className="lead",
                ),
            ], style={"text-align":"center",  "padding": "10px"})
        ], className="three columns"),

        html.Div([
            dbc.Jumbotron(           
            [
                html.H3(f"{int(daily_us_df['hospitalizedCumulative'][0]):,}", className="display-4"),
                html.P(
                        "Hospitalized cases",
                        className="lead",
                ),
            ],style={"text-align":"center",  "padding": "10px"} )
        ], className="three columns"),

        html.Div([
            dbc.Jumbotron(           
            [
                html.H3(f"{int(daily_us_df['recovered'][0]):,}", className="display-4"),
                html.P(
                        "Recovered cases",
                        className="lead",
                ),
            ], style={"text-align":"center", "padding": "10px"} )
        ], className="three columns"),
        
        html.Div([
            dbc.Jumbotron(           
            [
                html.H3(f"{int(daily_us_df['death'][0]):,}", className="display-4"),
                html.P(
                    "Fatal cases",
                    className="lead",
                ),

            ], style={"text-align":"center",  "padding": "10px"})
        ], className="three columns"),

    ], style={"width":"90%", "margin": "auto"}),

    #-------------------------- SECOND PART: 5 CHARTS, 2 ABOVE, 3 BELOW [NUMBERS OF WHOLE USA] -------------------------------------
 
    dbc.Jumbotron(    
        [
            html.Div([ 
                html.H2("Global Overview: USA Reported Cases"),
                html.P("These charts show the reported numbers for the whole USA from the inception date. They are collected on a daily basis and updated regularly each day at 20:00 CT. All the charts are interactive, you can hover over it to see the details or/and filter out a trace by clicking on its legend.", style={'text-align': 'center', "font-size":"12px", "margin-bottom": "20px"}),
            ], className = "twelve columns", style={'text-align': 'center'}),

            html.Div([  
                dbc.Jumbotron([ # linechart: Cummulative progresion in time
                    dcc.Graph(figure=cumulative_linechart_us()),
                    ], className = "seven columns", style={"padding": "0px"}),

                dbc.Jumbotron([ # barchart: Absolute numbers
                    dcc.Graph(figure=cumulative_barchart_us()),
                    ], className = "five columns", style={"padding": "0px"}),
            ]),

            html.Div([
                dbc.Jumbotron([ # pie chart: Total tests
                    dcc.Graph(figure=total_tests_pie())
                    ], className = "three columns", style={"padding": "0px"}), 

                dbc.Jumbotron([ # line chart: Daily increase
                    dcc.Graph(figure=hosp_death_daily_increase())
                    ], className = "six columns", style={"padding": "0px"}),

                dbc.Jumbotron([ # bar chart: Hospitalization
                    dcc.Graph(figure=hospitalized())
                    ], className = "three columns", style={"padding": "0px"}),
            ]),
    ], className = "twelve columns"),

    #-------------------------- THIRD PART: 4 CHARTS + DATE-PICKER CALLBACK [NUMBERS FOR STATES] -------------------------------------

    dbc.Jumbotron(           
        [
            html.Div([
                html.H3("Daily Tracker of Reported Cases by State", style={"text-align":"center"}),
                html.P("These charts show the progression of COVID-19 by state on a daily basis. The choropleth displays the density of reported cases, the pie shows a simple distribution across all the states and the corelation plots the dependency between positive cases and population of the particular state. The sunburts chart down left is quite interesting, it sums up all the reported cases by regions, divisions, and states, weights is out by the number of deaths and colors the region based on that result. You can hover over a region to see the details or click to expand it.",  style={"font-size": "12px"}),
                html.P("Pick up a date to see the progression in a particular point in time."),
                # html.Br(),
                html.Div([
                dcc.DatePickerSingle(
                    id='my-date-picker-single',
                    min_date_allowed=datetime.date(2020, 1, 22),
                    max_date_allowed=set_starting_date(),
                    date=str(set_starting_date()) 
                ),
                ],  style={"font-size": "14px"} ),
               
                html.Br(),
            ], style={'text-align': 'center', "margin-bottom": "30px"}, className = "twelve columns"),

            html.Div([
                dbc.Jumbotron([# left up chart: Map
                    dcc.Graph(id ='usa_map')
                    ], className = "seven columns",  style={"padding": "0px"}),

                dbc.Jumbotron([ # right up chart: Pie
                    dcc.Graph(id ='us_pie')
                    ], className = "five columns", style={"padding": "0px"}),
            ]), 

            html.Div([
                dbc.Jumbotron([ # left down chart: Regions and divisions
                    # dcc.Graph(figure = distribution_by_divisions())
                    dcc.Graph(id = "us_sunburst")
                    ], className = "seven columns", style={"padding": "0px"}),
                
                dbc.Jumbotron([ # right down chart: Scatter corelation
                    dcc.Graph(id = "us_corel")
                    ], className = "five columns", style={"padding": "0px"}),
            ]),

        ], className = "twelve columns"),


    #-------------------------- FOURTH PART: 2 WIDE BARCHARTS [NUMBERS FOR STATES] -------------------------------------
    
    dbc.Jumbotron(
        [
            html.Div([
                html.H3("Reported Cases by State", style={"text-align":"center"}),
                html.P("These humble barcharts represent the categorical data for each state. The mortality chart is calculated as a ration between reported positive  and fatal cases showing the percentage of infected people that actually died. The higher the number, the worse the situation in the particular state even though the state might have very few cases in absolut numbers.", style={"font-size": "12px"}),
                # html.P("You can hover over a figure in the graph to see the details or/and filter out a trace by clicking on its legend. You can also pick up a date to see the COVID progression in time."),
            ], style={'text-align': 'center', "margin-bottom": "30px"}, className = "twelve columns"),

            dbc.Jumbotron([ # first barchart: Population and positive cases
                dcc.Graph(figure=scatter_bar_population_positive())
            ], className = "twelve columns",  style={"padding": "0px"}),

            dbc.Jumbotron([ # second barchart: Mortality
                dcc.Graph(figure=create_mortality_barchart())
            ], className = "twelve columns",  style={"padding": "0px"}),

        ], className = "twelve columns"),           

    #-------------------------- FIFTH PART: TABLE WITH BARCHART + CALLBACK [NUMBERS FOR STATES] -------------------------------------

    dbc.Jumbotron([
        html.Div([ # the interactive table
            html.H3("Reported Cases: Tabular Data Overwiev", style={"text-align":"center"}),
            html.Br(),
            html.P("This interactive table allows you to filter out data using arithmetic operators. If you for example want to see only states with positive cases above 1000, just type '> 1000' in the column 'Positive'. You can also use the checkboxes on the left to plot the data for particular state in the barchart on the right hand side of the table.", style={"text-align": "center", "font-size": "12px"}),
            html.Br(),
            dash_table.DataTable(
                id='datatable_id',
                data=current_state_df.to_dict('records'),
                columns=rename_datatable_columns(), # here i use the renamed headers 
                editable=False,
                filter_action="native",
                sort_action="native",
                sort_mode="multi",                row_selectable="multi",
                row_deletable=False,
                selected_rows=[],
                page_action='native',
                page_size = 11,
                fixed_rows={ 'headers': True, 'data': 0 },
                virtualization=False,
                style_cell={
                    'minWidth': '40px', 'width': '60px', 'maxWidth': 'px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
            },)
        ], className="eight columns",  style={"text-align": "center", "font-size": "12px"}),

        html.Div([ # horizontal barchart bound to the table 
            html.H3("Charting Tabular Data", style={"text-align": "center"}),
            html.Br(),
            html.P("Use dropdown to choose the case.", style={"text-align": "center", "font-size": "12px"}),
            dcc.Dropdown(id='dropval',
                            options=[
                                {'label': 'Tested', 'value': 'totalTestResults'}, 
                                {'label': 'Positive', 'value': 'positive'},
                                {'label': 'Hospitalized', 'value': 'hospitalized'},
                                {'label': 'Recovered', 'value': 'recovered'},
                                {'label': 'Fatal', 'value': 'death'},
                            ],
                            value='positive',
                            multi=False,
                            clearable=False
                        ),
            html.Br(),
            dcc.Graph(id='horizontal_barchart', style={"padding": "0px"}),            
        ], className = "four columns"),

    ], className="twelve columns"),

     html.Footer([
        html.P("Primary data source: CovidTracking API. Created by Lukash K. © 2020.", style={"text-align":"center"}),
        html.P(html.A('Buy me a drink and support this project.', href='https://www.buymeacoffee.com/nirvikalpa'), style={"text-align":"center"}),
    ], style={"margin": "1px auto 0 auto"})

    ], className = "row", style={"width":"80%", "margin": "auto"}
)


@app.callback(
    [Output(component_id='usa_map', component_property='figure'),
    Output(component_id='us_pie', component_property='figure'),
    Output(component_id='us_corel', component_property='figure'),
    Output(component_id='us_sunburst', component_property='figure')],
    [Input(component_id='my-date-picker-single', component_property='date')],)
def update_output(date):
    """ Function for updating Map, Pie, Sunburst and Scatter charts through the date-picker callback button """  

    if date is None:
        raise PreventUpdate
    else:
        date = date.replace("-", "")
        qdf = df.query("date=={}".format(date))

        states = qdf["state"]
        posi = qdf["positive"]

        # building the Map
        fig_map = go.Figure(data=go.Choropleth( locations=qdf["state"],
                                                z=qdf["positive"].astype(int),
                                                autocolorscale=True,
                                                colorscale='Bluered',
                                                colorbar_title="Positive",
                                                locationmode='USA-states'))
        fig_map.update_layout(  title_text='Density by State',
                                height = 600,
                                geo = dict(
                                    scope='usa',
                                    projection=go.layout.geo.Projection(type = 'albers usa'),
                                    # showlakes=True, # lakes
                                    lakecolor='rgb(255, 255, 255)'
                                ),
                                margin=dict(
                                    l=1,
                                    r=1,
                                ),)

        # building the Pie
        fig_pie = px.pie(   qdf, 
                            values='positive', 
                            names='state', 
                            title='Distribution by State')
        fig_pie.update_layout(  height = 600, 
                                legend=dict(
                                    x=1,
                                    y=0.7,
                                ),
                                margin=dict(
                                    b=150,
                                ),
                            )
        fig_pie.update_traces(domain_x=[0, 0.7]) # positiong of the chart itself, without the title

        # building the Corelation scatter
        fig_scatter = go.Figure(data=go.Scatter(x=qdf["pop"], 
                                                y=qdf["positive"], 
                                                mode='markers', 
                                                text=qdf['state name']))
        fig_scatter.update_layout(  plot_bgcolor = 'rgba(0,0,0,0)', 
                                    title='Corelation Chart', 
                                    autosize=True,
                                    height=600,
                                    margin=dict(
                                        l=10,
                                        r=10
                                    ),)

        # building the Sunburst
        print(date)
        date_df = create_df_for_date(int(date))
        print(date_df)
        fig_sunburst = px.sunburst( date_df,
                                path=["total positive", "region", "division", "state"], 
                                values='positive', 
                                color="death", 
                                color_continuous_scale="Rdbu")
        fig_sunburst.update_layout( height=600, 
                                title="Positive Cases by Region - Click To Expand",
                                margin=dict(
                                            l=1,
                                            r=1,
                                            b=70,
                                            t=100,
                                )
                                )

    return (fig_map, fig_pie, fig_scatter, fig_sunburst)


@app.callback(
    Output('horizontal_barchart', 'figure'),  
    [Input('datatable_id', 'selected_rows'),
    Input('dropval', 'value')])
def update_data(selected_rows, dropval):
    """ Function for updating the Horizontal Barchar based on what states are selected in the table and what is picked in dropdown """

    # update the table
    if len(selected_rows) == 0:
        grouped_sel_df = current_state_df[current_state_df['state'].isin(["NJ", "IL", "MA", "TX", "PA", "KS", "OH", "UT", "VI", "VT"])] 
    else:
        grouped_sel_df = current_state_df[current_state_df.index.isin(selected_rows)] 

    # update the X-axis labels based on the dropdown selection
    if dropval == "positive": xaxis_label = "Positive"
    elif dropval == "totalTestResults": xaxis_label = "Tested"
    elif dropval == "hospitalized": xaxis_label = "Hospitalized"
    elif dropval == "recovered": xaxis_label = "Recovered"
    elif dropval == "death": xaxis_label = "Fatal"

    # build the Horizontal Barchart
    bar_chart = px.bar(
                        data_frame=grouped_sel_df,
                        y='state',
                        x=dropval, # here comes the argument from the dropdown menu
                        color='state',
                        orientation='h')

    bar_chart.update_layout(plot_bgcolor = 'rgba(0,0,0,0)',
                            title=f'Reported Cases', 
                            showlegend=False,
                            legend=dict(
                                x=0.01,
                                y=1.0,
                                bgcolor='rgba(255, 255, 255, 0)',
                                bordercolor='rgba(255, 255, 255, 0)'
                            ),
                            xaxis=dict(title=f"{xaxis_label} Cases"),
                            yaxis=dict(title="States"))
    return (bar_chart)


if __name__ == '__main__':
    app.run_server()




