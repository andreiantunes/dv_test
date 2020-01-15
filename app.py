import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
from plotly import tools

######################################################Data##############################################################

df = pd.read_csv('data/table.csv')

Europe = ['Albania','Armenia','Austria','Azerbaijan','Belarus','Belgium','Bulgaria','Croatia','Cyprus',
          'Czech Republic','Denmark','Estonia','Finland','France','Georgia','Germany','Greece','Hungary',
          'Iceland','Ireland','Italy','Kazakhstan','Latvia','Lithuania','Luxembourg','Malta','Moldova',
          'Netherlands','Norway','Poland','Portugal','Romania','Russian Federation','Slovak Republic',
          'Slovenia','Spain','Sweden','Switzerland','Turkey','Ukraine','United Kingdom']

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in Europe]

continent_options = [dict(label=continent, value=continent) for continent in df['Continent_Name'].unique()]


##################################################APP###############################################################

app = dash.Dash(__name__)

app.layout = html.Div([

    html.Div([
        html.H1(
            "European Tourism",
            style={"margin-bottom": "0px"},
        ),

        html.H3(
            "An Overview", style={"margin-top": "0px"}
        )
    ], className='Title'),

    html.Div([

        html.Div([
            html.Label('Country Choice'),
            dcc.Dropdown(
                id='country_drop',
                options=country_options,
                value=['Portugal', 'France'],
                multi=True
            ),

            html.Br(),

            html.Label('Continent Choice'),
            dcc.Dropdown(
                id='continent_drop',
                options=continent_options,
                value=['Europe','World'],
                multi=True
            ),

            html.Br(),

            html.Label('Year Slider'),
            dcc.Slider(
                id='year_slider',
                min=df['Years'].min(),
                max=2016,
                marks={str(i): '{}'.format(str(i)) for i in [2000, 2002, 2004, 2006, 2008, 2010, 2012, 2014, 2016]},
                value=2016,
                step=1,
                included=False
            ),
        ], className='column2 pretty'),

        html.Div([dcc.Graph(id='bubbles_graph')], className='column1 pretty')
    ], className='row'),

    html.Div([

        html.Div([dcc.Graph(id='line_graph')], className='column2 pretty'),

        html.Div([dcc.Graph(id='choropleth')], className='column1 pretty')

    ], className='row'),

    html.Div([

        html.Div([dcc.Graph(id='radar_graph')], className='column3 pretty'),

        html.Div([dcc.Graph(id='subplot_graph')], className='column4 pretty')

    ], className='row')

])

######################################################Callbacks#########################################################

@app.callback(
    [
        Output("choropleth", "figure"),
        Output("line_graph", "figure"),
        Output("bubbles_graph", "figure"),
        Output("radar_graph", "figure"),
        Output("subplot_graph", "figure")
    ],
    [
        Input("year_slider", "value"),
        Input("country_drop", "value"),
        Input("continent_drop", "value")
    ]
)
def plots(year, countries, continent):

    #############################################First Choropleth######################################################
    df_EU = df.loc[df['Country_Name'].isin(Europe)]
    df_EU_0 = df_EU.loc[df_EU['Years']== year]
    data_choropleth = dict(type='choropleth',
                           locations=df_EU_0['Country_Name'],
                           locationmode='country names',
                           text=df_EU_0['Country_Name'],
                           colorscale='YlGnBu',
                           colorbar=dict(title='Arrivals'),
                           #hovertemplate='Country: %{text} <br>' + str(gas.replace('_', ' ')) + ': %{z}',
                           z=df_EU_0['Arrivals'])

    layout_choropleth = dict(geo=dict(scope='europe',
                                      projection={'type': 'equirectangular'},
                                      bgcolor='#f9f9f9',
                                      showframe = False
                                      ),
                             title=dict(text='Arrivals',
                                        x=.5  # Title relative position according to the xaxis, range (0,1)
                                        ),
                             paper_bgcolor='#f9f9f9')

    ############################################Second Lines Plot######################################################
    dataContinents = df[df.Country_Name.isna()]

    data_line = [dict(type = 'scatter',
                         x = dataContinents.loc[dataContinents['Continent_Name'] == country]['Years'],
                         y = dataContinents.loc[dataContinents['Continent_Name'] == country]['Receipts_PCapita'],
                         name = country) for country in continent]

    layout_line = dict(title = dict(text = 'Tourism GDP per capita, per continent ',y=0.9,x=0.5),
                            xaxis = dict(title = 'Year'),
                            yaxis = dict(title = 'Tourism GDP Per Capita'),
                            paper_bgcolor = 'white',
                            template='plotly_white',
                            legend = dict(orientation='h',yanchor='top',xanchor='center',y=-0.3,x=0.5))

     ############################################Third Bubbles Plot#####################################################
    dataBubble = df.dropna()
    dataBubble.sort_values(by ='Years', inplace = True)
    data_bubble = px.scatter(dataBubble.loc[dataBubble['Country_Name'].isin(countries)], x="GDP", y="Receipts_PCapita",
                             animation_frame="Years", animation_group="Country_Name",
                             size="Ratio GDP", hover_name="Country_Name", color="Country_Name",
                             log_x=True, size_max=40, range_x=[300, 120000], range_y=[0, 11000])

    layout_bubble = data_bubble.update_layout(title=dict(text='Tourism related to GDP, per country', y=0.9, x=0.5),
                                              xaxis=dict(title='GDP Per Capita'),
                                              yaxis=dict(title='Tourism GDP Per Capita'),
                                              paper_bgcolor='white',
                                              template='plotly_white'

                                              )

    data_bubble.for_each_trace(lambda t: t.update(name=t.name.replace("Country_Name=", "")))
    ############################################Forth Radar Plot######################################################

    labels = ['GDP_N', 'Expenditures_N', 'PopTotal_N', 'Arrivals_N', 'Departure_N', 'GDP_N']
    data_radar =[]
    color_array = ["#999999", "#E69F00", "#56B4E9", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7", '#9a6a00',
                   '#0047e6','#00523b', '#893c00']
    color_numb = 0

    for country in countries:
        dataradar = df[['GDP_N', 'Expenditures_N', 'PopTotal_N', 'Arrivals_N', 'Departure_N']].loc[
            (df['Years'] == year) & (df['Country_Name'] == country)]
        values = dataradar.values.flatten().tolist()
        values += values[:1]
        data_radar.append(dict(type='scatterpolar',
                               r=values,
                               theta=labels,
                               fill='toself',
                               name=country,
                               line_color= color_array[color_numb],
                               mode='lines'
                               ))
        color_numb += 1

    layout_radar = dict(
        title='Radar Chart',
        font=dict(
            # family = 'Arial, sans-serif;',
            size=12,
            color='#000'
        ),
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[-3, 3]
            )),
        showlegend=True
    )

    ############################################Fifth Bar Plot##########################################################
    titles = ['Title1', 'Title2']
    plot = make_subplots(rows=1,
                         cols=2,
                         subplot_titles=titles,
                         specs= [[{}, {}]], shared_xaxes = True,
                         shared_yaxes=False, vertical_spacing=0.001
                         )


    ############################################Fifth Bar Plot##########################################################
    data_bar = []
    for country in countries:
        df_bar = df.loc[df['Country_Name'] == country]

        x_bar = df_bar['Country_Name']
        y_bar = (df_bar.loc[df_bar['Years'] == year]['Jobs_per_tourist'])
        plot.append_trace(go.Bar(
            x=y_bar,
            y=x_bar,
            marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(
                    color='rgba(50, 171, 96, 1.0)',
                    width=1),
            ),
            orientation='h',
            showlegend= False
        ), 1, 1)

    ############################################Sixth Markers Plot######################################################

    data_markers = []
    for country in countries:
        df_markers = df.loc[(df['Country_Name'] == country)]

        plot.append_trace(go.Bar(
            x=df_markers.loc[df_markers['Years']==year]['Cost_of_oneJob'],
            y=df_markers['Country_Name'],
            marker=dict(
                color='rgba(50, 171, 96, 0.6)',
                line=dict(
                    color='rgba(50, 171, 96, 1.0)',
                    width=1),
            ),
            orientation='h',
            showlegend=False
        ), 1, 2)


    plot.update_layout(
        title='UPDATE NAME OF THE PLOT',
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            domain=[0, 0.85],
        ),
        yaxis2=dict(
            showgrid=False,
            showline=True,
            showticklabels=False,
            linecolor='rgba(102, 102, 102, 0.8)',
            linewidth=2,
            domain=[0, 0.85],
        ),
        xaxis=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0, 0.42],
        ),
        xaxis2=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0.47, 1],
            side='top',
            dtick=25000,
        ),
        legend=dict(x=0.029, y=1.038, font_size=10),
        margin=dict(l=100, r=20, t=70, b=70),
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
    )

    return go.Figure(data=data_choropleth, layout=layout_choropleth), \
           go.Figure(data=data_line, layout=layout_line), \
           go.Figure(data=data_bubble, layout=layout_bubble), \
           go.Figure(data=data_radar, layout=layout_radar), \
           plot


if __name__ == '__main__':
    app.run_server(debug=True)

