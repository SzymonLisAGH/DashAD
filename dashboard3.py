
from datetime import datetime
from email.policy import default
from msilib.schema import Component
from sre_parse import State
from ssl import Options
from turtle import color, width
from typing import Type
import dash
from dash.dependencies import Output, Input
from dash import dcc
from dash import html
import plotly
import plotly.graph_objs as go
import plotly.express as px
import logging
import sys
import traceback
import pickle
import pandas as pd
import numpy as np
from sqlalchemy import null
import dash_daq as daq
import dash_bootstrap_components as dbc

categories={}



def FixDatetime(str):
    str = str.replace("_"," ")
    return str.replace("/","-")

df_main = pd.read_csv('data_ad.csv',';')
df_main['checking_time']=df_main['checking_time'].apply(FixDatetime)
df_main['checking_time']=pd.to_datetime(df_main['checking_time'])
df_main.set_index('checking_time',inplace=True)

df_cat=pd.read_csv('data_ad_spis.csv',';',nrows=64)
for cat in df_cat.Category.unique():
    if cat=="INDEX":
        continue
    categories[cat]=[]
for idx,row in df_cat.iterrows():
    if row[1]=="INDEX":
        continue
    categories[row[1]].append({'label' : row[2],'value':row[0]})
df_cat.set_index('Data',inplace=True)

singledate=dcc.DatePickerSingle(
                        id='single-picker',
                        min_date_allowed=datetime(2022, 5, 1),
                        max_date_allowed=datetime(2025, 12, 31),
                        initial_visible_month=datetime(2022, 5, 1),
                        date=datetime(2022, 5, 19).date(),
                        display_format='MMM Do, YY',
                        month_format='MMMM, YYYY'
                    )

multidate = dcc.DatePickerRange(
        id='multi-picker',  # ID to be used for callback
        calendar_orientation='horizontal',  # vertical or horizontal
        day_size=39,  # size of calendar image. Default is 39
        end_date_placeholder_text="Return",  # text that appears when no end date chosen
        with_portal=False,  # if True calendar will open in a full screen overlay portal
        first_day_of_week=0,  # Display of calendar when open (0 = Sunday, 1 = monday)
        reopen_calendar_on_clear=True,
        is_RTL=False,  # True or False for direction of calendar
        clearable=True,  # whether or not the user can clear the dropdown
        number_of_months_shown=1,  # number of months shown when calendar is open
        min_date_allowed=datetime(2022, 5, 1),  # minimum date allowed on the DatePickerRange component
        max_date_allowed=datetime(2025, 12, 31),  # maximum date allowed on the DatePickerRange component
        initial_visible_month=datetime(2022, 5, 1),  # the month initially presented when the user opens the calendar
        start_date=datetime(2022, 5, 19).date(),
        end_date=datetime(2022, 5, 27).date(),
        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
        minimum_nights=0,  # minimum number of days between start and end date
        persistence=True,
        persisted_props=['start_date'],
        persistence_type='session',  # session, local, or memory. Default is 'local'
        updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered
        )

def GenerateGraph(data,start,end):
        dfm = df_main.loc[start:end]
        dfc = df_cat.loc[data]
        figure={
                'data' : [{'x':dfm.index, 'y':dfm[data], 'type' : 'bar', 'name' : dfc['Label']}],
                'layout' : {
                    'title' : f'{dfc["Label"]}'
                } 
             }
        return figure

def CreateWebPage():
    external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
    app.layout = html.Div([
        html.H1("Dashboard Worldometer Data", style={'textAlign': 'center'}),
        html.P("Created by:     Agnieszka Wellian, Filip Olszowski, Szymon Lis", style={'textAlign': 'center','fontStyle':'italic'}),
        dcc.Interval(
            id = 'graphs-update',
            interval = 1000,
            n_intervals = 0
        ),
        dcc.Tabs(id='main_tabs',value='POPULATION',children=[
            dcc.Tab(label='Population',value='POPULATION', children=[
                html.Div(children=[
                    html.Br(),
                   dcc.Dropdown(id='data_dropdown1',style={"width":"80%"})
                    ],  style={'width': '49%', 'display': 'inline-block'}
                ),

                html.Div(children=[
                    html.Br(),
                    dcc.DatePickerRange(
                        id='multi-picker1',  # ID to be used for callback
                        calendar_orientation='horizontal',  # vertical or horizontal
                        day_size=39,  # size of calendar image. Default is 39
                        end_date_placeholder_text="Return",  # text that appears when no end date chosen
                        with_portal=False,  # if True calendar will open in a full screen overlay portal
                        first_day_of_week=0,  # Display of calendar when open (0 = Sunday, 1 = monday)
                        reopen_calendar_on_clear=True,
                        is_RTL=False,  # True or False for direction of calendar
                        clearable=True,  # whether or not the user can clear the dropdown
                        number_of_months_shown=1,  # number of months shown when calendar is open
                        min_date_allowed=datetime(2022, 5, 1),  # minimum date allowed on the DatePickerRange component
                        max_date_allowed=datetime(2025, 12, 31),  # maximum date allowed on the DatePickerRange component
                        initial_visible_month=datetime(2022, 5, 1),  # the month initially presented when the user opens the calendar
                        start_date=datetime(2022, 5, 19).date(),
                        end_date=datetime(2022, 5, 27).date(),
                        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                        minimum_nights=0,  # minimum number of days between start and end date
                        persistence=True,
                        persisted_props=['start_date'],
                        persistence_type='session',  # session, local, or memory. Default is 'local'
                        updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered
                        )
                    ],  style={'width': '49%', 'float': 'right','display': 'inline-block'}
                ),

                html.Br(),
                dcc.Graph(id='graph1')
            ]),

            dcc.Tab(label="Finances",value="MONEY", children=[
                html.Div(children=[
                    html.Br(),
                   dcc.Dropdown(id='data_dropdown2',style={"width":"80%"})
                    ],  style={'width': '49%', 'display': 'inline-block'}
                ),

                html.Div(children=[
                    html.Br(),
                    dcc.DatePickerRange(
                        id='multi-picker2',  # ID to be used for callback
                        calendar_orientation='horizontal',  # vertical or horizontal
                        day_size=39,  # size of calendar image. Default is 39
                        end_date_placeholder_text="Return",  # text that appears when no end date chosen
                        with_portal=False,  # if True calendar will open in a full screen overlay portal
                        first_day_of_week=0,  # Display of calendar when open (0 = Sunday, 1 = monday)
                        reopen_calendar_on_clear=True,
                        is_RTL=False,  # True or False for direction of calendar
                        clearable=True,  # whether or not the user can clear the dropdown
                        number_of_months_shown=1,  # number of months shown when calendar is open
                        min_date_allowed=datetime(2022, 5, 1),  # minimum date allowed on the DatePickerRange component
                        max_date_allowed=datetime(2025, 12, 31),  # maximum date allowed on the DatePickerRange component
                        initial_visible_month=datetime(2022, 5, 1),  # the month initially presented when the user opens the calendar
                        start_date=datetime(2022, 5, 19).date(),
                        end_date=datetime(2022, 5, 27).date(),
                        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                        minimum_nights=0,  # minimum number of days between start and end date
                        persistence=True,
                        persisted_props=['start_date'],
                        persistence_type='session',  # session, local, or memory. Default is 'local'
                        updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered
                        )
                    ],  style={'width': '49%', 'float': 'right','display': 'inline-block'}
                ),
                html.Br(),
                dcc.Graph(id='graph2')
            ]),

            dcc.Tab(label="Production",value="PRODUCTION", children=[
                html.Div(children=[
                    html.Br(),
                   dcc.Dropdown(id='data_dropdown3',style={"width":"80%"})
                    ],  style={'width': '49%', 'display': 'inline-block'}
                ),

                html.Div(children=[
                    html.Br(),
                    dcc.DatePickerRange(
                        id='multi-picker3',  # ID to be used for callback
                        calendar_orientation='horizontal',  # vertical or horizontal
                        day_size=39,  # size of calendar image. Default is 39
                        end_date_placeholder_text="Return",  # text that appears when no end date chosen
                        with_portal=False,  # if True calendar will open in a full screen overlay portal
                        first_day_of_week=0,  # Display of calendar when open (0 = Sunday, 1 = monday)
                        reopen_calendar_on_clear=True,
                        is_RTL=False,  # True or False for direction of calendar
                        clearable=True,  # whether or not the user can clear the dropdown
                        number_of_months_shown=1,  # number of months shown when calendar is open
                        min_date_allowed=datetime(2022, 5, 1),  # minimum date allowed on the DatePickerRange component
                        max_date_allowed=datetime(2025, 12, 31),  # maximum date allowed on the DatePickerRange component
                        initial_visible_month=datetime(2022, 5, 1),  # the month initially presented when the user opens the calendar
                        start_date=datetime(2022, 5, 19).date(),
                        end_date=datetime(2022, 5, 27).date(),
                        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                        minimum_nights=0,  # minimum number of days between start and end date
                        persistence=True,
                        persisted_props=['start_date'],
                        persistence_type='session',  # session, local, or memory. Default is 'local'
                        updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered
                        )
                    ],  style={'width': '49%', 'float': 'right','display': 'inline-block'}
                ),
                html.Br(),
                dcc.Graph(id='graph3')
            ]),

            dcc.Tab(label="Environment",value="ENVIRONMENT", children=[
                html.Div(children=[
                    html.Br(),
                   dcc.Dropdown(id='data_dropdown4',style={"width":"80%"})
                    ],  style={'width': '49%', 'display': 'inline-block'}
                ),

                html.Div(children=[
                    html.Br(),
                    dcc.DatePickerRange(
                        id='multi-picker4',  # ID to be used for callback
                        calendar_orientation='horizontal',  # vertical or horizontal
                        day_size=39,  # size of calendar image. Default is 39
                        end_date_placeholder_text="Return",  # text that appears when no end date chosen
                        with_portal=False,  # if True calendar will open in a full screen overlay portal
                        first_day_of_week=0,  # Display of calendar when open (0 = Sunday, 1 = monday)
                        reopen_calendar_on_clear=True,
                        is_RTL=False,  # True or False for direction of calendar
                        clearable=True,  # whether or not the user can clear the dropdown
                        number_of_months_shown=1,  # number of months shown when calendar is open
                        min_date_allowed=datetime(2022, 5, 1),  # minimum date allowed on the DatePickerRange component
                        max_date_allowed=datetime(2025, 12, 31),  # maximum date allowed on the DatePickerRange component
                        initial_visible_month=datetime(2022, 5, 1),  # the month initially presented when the user opens the calendar
                        start_date=datetime(2022, 5, 19).date(),
                        end_date=datetime(2022, 5, 27).date(),
                        display_format='MMM Do, YY',  # how selected dates are displayed in the DatePickerRange component.
                        month_format='MMMM, YYYY',  # how calendar headers are displayed when the calendar is opened.
                        minimum_nights=0,  # minimum number of days between start and end date
                        persistence=True,
                        persisted_props=['start_date'],
                        persistence_type='session',  # session, local, or memory. Default is 'local'
                        updatemode='singledate',  # singledate or bothdates. Determines when callback is triggered
                        )
                    ],  style={'width': '49%', 'float': 'right','display': 'inline-block'}
                ),
                html.Br(),
                dcc.Graph(id='graph4')
            ]),

            dcc.Tab(label="Resources",value="RESOURCES", children=[
                html.Div(children=[
                    dcc.Markdown('''
                        ### Energy and Resources Data ###
                    ''')
                    ],  style={'width': '49%', 'display': 'inline-block'}
                ),

                html.Div(children=[
                    html.Br(),
                    singledate
                    ],  style={'width': '49%', 'float': 'right','display': 'inline-block'}
                ),

                html.Div(dcc.Slider(0,24,
                    step=None,
                    id='slider-hours',
                    value=24,
                    marks={
                        0:{'label':'00:00'},
                        1:{'label':'01:00'},
                        2:{'label':'02:00'},
                        3:{'label':'03:00'},
                        4:{'label':'04:00'},
                        5:{'label':'05:00'},
                        6:{'label':'06:00'},
                        7:{'label':'07:00'},
                        8:{'label':'08:00'},
                        9:{'label':'09:00'},
                        10:{'label':'10:00'},
                        11:{'label':'11:00'},
                        12:{'label':'12:00'},
                        13:{'label':'13:00'},
                        14:{'label':'14:00'},
                        15:{'label':'15:00'},
                        16:{'label':'16:00'},
                        17:{'label':'17:00'},
                        18:{'label':'18:00'},
                        19:{'label':'19:00'},
                        20:{'label':'20:00'},
                        21:{'label':'21:00'},
                        22:{'label':'22:00'},
                        23:{'label':'23:00'},
                        24:{'label':'00:00'},
                    },
                ), style={'width': '100%'}),

                html.Div(children=[
                    dcc.Graph(id='energy',
                        config={'displayModeBar':False},
                        className='card')

                    #html.H6("Earth energy demand vs Solar energy striking earth today", style={'textAlign': 'center'}),

                    #dbc.Progress(value=50, id='energy_progress' )
                    ],  style={'width': '40%', 'display': 'inline-block'}
                ),

                html.Div(children=[
                    html.Div(children=[
                        html.Br(),
                        html.P("Days to the end of oil"),
                        daq.LEDDisplay(
                        id="days_oil",
                        value="0",
                        color="#141313",
                        backgroundColor="#ffffff",
                        size=30,
                        ),
                    ],style={'width': '32%','display': 'inline-block'}),

                    html.Div(children=[
                        html.Br(),
                        html.P("Days to the end of natural gas"),
                        daq.LEDDisplay(
                        id="days_gas",
                        value="0",
                        color="#141313",
                        backgroundColor="#ffffff",
                        size=30,
                        ),
                    ],style={'width': '32%','display': 'inline-block'}),

                    html.Div(children=[
                        html.Br(),
                        html.P("Days to the end of coal"),
                        daq.LEDDisplay(
                        id="days_coal",
                        value="0",
                        color="#141313",
                        backgroundColor="#ffffff",
                        size=30,
                        ),
                    ],style={'width': '32%','display': 'inline-block'}),
                    
                    dcc.Graph(id = 'resources_left')

                    ],  style={'width': '55%', 'float': 'right','display': 'inline-block'}
                ),
   
            ]),
        ])
    ])

    @app.callback(
        Output(component_id='graph1', component_property="figure"),
        [
        Input(component_id ='data_dropdown1', component_property="value"),
        Input(component_id = 'multi-picker1', component_property="start_date"),
        Input(component_id = 'multi-picker1', component_property="end_date"),
        ]
    )
    def update_graph(data,start,end):
        return GenerateGraph(data,start,end)

    @app.callback(
        Output(component_id='graph2', component_property="figure"),
        [
        Input(component_id ='data_dropdown2', component_property="value"),
        Input(component_id = 'multi-picker2', component_property="start_date"),
        Input(component_id = 'multi-picker2', component_property="end_date"),
        ]
    )
    def update_graph(data,start,end):
        return GenerateGraph(data,start,end)

    @app.callback(
        Output(component_id='graph3', component_property="figure"),
        [
        Input(component_id ='data_dropdown3', component_property="value"),
        Input(component_id = 'multi-picker3', component_property="start_date"),
        Input(component_id = 'multi-picker3', component_property="end_date"),
        ]
    )
    def update_graph(data,start,end):
        return GenerateGraph(data,start,end)

    @app.callback(
        Output(component_id='graph4', component_property="figure"),
        [
        Input(component_id ='data_dropdown4', component_property="value"),
        Input(component_id = 'multi-picker4', component_property="start_date"),
        Input(component_id = 'multi-picker4', component_property="end_date"),
        ]
    )
    def update_graph(data,start,end):
        return GenerateGraph(data,start,end)

    @app.callback(Output('data_dropdown1', 'options'),
                Input('main_tabs', 'value'))
    def update_dropdown(val):
        return categories[val]

    @app.callback(Output('data_dropdown2', 'options'),
                Input('main_tabs', 'value'))
    def update_dropdown(val):
        return categories[val]

    @app.callback(Output('data_dropdown3', 'options'),
                Input('main_tabs', 'value'))
    def update_dropdown(val):
        return categories[val]

    @app.callback(Output('data_dropdown4', 'options'),
                Input('main_tabs', 'value'))
    def update_dropdown(val):
        return categories[val]

    @app.callback(
    [
        Output('energy', 'figure'),
        Output('days_oil', 'value'),
        Output('days_gas', 'value'),
        Output('days_coal', 'value'),
        Output('resources_left','figure'),
    ],
    [
        Input('single-picker','date'),
        Input('slider-hours','value')
     ]
    )
    def update_pie_chart(date,slider_val):
        hours=['00:00','00:59','01:59','02:59','03:59','04:59','05:59','06:59','07:59','08:59','09:59','10:59','11:59','12:59','13:59',
        '14:59','15:59','16:59','17:59','18:59','19:59','20:59','21:59','22:59','23:59']
        labels = ['Renewable Sources [MWh]', "Non-Renewable Sources [MWh]"]
        dfm = df_main.loc[date]
        dfm=dfm.loc[date+" 00:00":date+" "+hours[slider_val]].max(axis=0)
        values = [dfm['renewable_sources'],dfm['non-renewable_sources']]
    
        ## using dash to make the pie chart
        fig1=go.Figure(data=[
            go.Pie(labels=labels,values=values,textinfo='label+value+percent',hole=.3)
        ])
        colors=['green','red']
        fig1.update_traces(marker = dict(colors=colors))
        title_='Energy Used Today :'
        total = dfm['renewable_sources']+dfm['non-renewable_sources']
        fig1.update_layout(title=f"{title_} {total} MWh")

        figure={
            'data':[
                {'x': ['Resource Left'], 'y':[dfm['oil_left']], 'type':'bar', 'name' : 'Oil [Barrels]'},
                {'x': ['Resource Left'], 'y':[dfm['natural_gas_left']], 'type':'bar', 'name' : 'Natural gas [BOE]'},
                {'x': ['Resource Left'], 'y':[dfm['coal_left']], 'type':'bar', 'name' : 'coal [BOE]'},
            ],
            'layout':{
                'title':'Resources Left'
            }
        }
        return fig1,dfm['days_to_the_end_of_oil'],dfm['days_to_the_end_of_natural_gas'],dfm['days_to_the_end_of_coal'],figure

    return app

def main():
    global received_flag,received_frame

    app = CreateWebPage()
    app.run_server(host='0.0.0.0')
    app.config.suppress_callback_exceptions = True

if __name__ == '__main__':
    main()