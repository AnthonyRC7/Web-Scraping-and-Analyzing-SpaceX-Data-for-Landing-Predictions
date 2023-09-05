import pandas as pd
import dash
import plotly.express as px
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

# Create the dash app
app = dash.Dash(__name__)
spacex_data = pd.read_csv("spacex_file.csv")

labels_dict = {"All Sites": "ALL", "CCAFS LC-40": "CCAFS LC-40", "KSC LC-39A": "KSC LC-39A",
               "VAFB SLC-4E": "VAFB SLC-4E", "CCAFS SLC-40": "CCAFS SLC-40"}

# Build dash app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 24}),
                                html.Br(),

                                html.Div([html.Label('Launch Site:'),
                                          dcc.Dropdown(
                                              id='site-dropdown',
                                              options=[
                                                  {'label': label, 'value': labels_dict[label]}
                                                  for label in labels_dict
                                              ],
                                              placeholder='Select a Launch Site here',
                                              value='ALL',
                                              searchable=True,
                                              style={'width': '80%', 'padding': '3px', 'font-size': 20,
                                                     'text-align-last': 'center'}
                                          )
                                          ]),

                                html.Br(),
                                # 1st graph
                                html.Div([
                                    html.Div(dcc.Graph(id='success-pie-chart'))
                                ]),
                                html.Br(),
                                html.Br(),
                                # Range Slider
                                html.Div([
                                    dcc.RangeSlider(
                                        id='payload-slider',
                                        min=0,
                                        max=10000,
                                        step=1000,
                                        marks={i: str(i) for i in range(0, 10001, 2500)},
                                        value=[spacex_data["Payload Mass (kg)"].min(),
                                               spacex_data["Payload Mass (kg)"].max()]
                                    ),
                                    # 2nd graph
                                    dcc.Graph(id='success-payload-scatter-chart')
                                ]),
                                ]
                      )


def get_pie_chart(entered_site):
    filtered_data = spacex_data[["Launch Site", "class"]]
    if entered_site == 'ALL':
        all_sites_pie_data = filtered_data.groupby("Launch Site")["class"].sum().reset_index()
        all_sites_pie_data = all_sites_pie_data.rename(columns={'class': 'count'})
        fig = px.pie(all_sites_pie_data, values='count',
                     names='Launch Site',
                     title='Total Success Launches by Site')

        return fig

    else:
        selected_data = filtered_data[filtered_data["Launch Site"] == str(entered_site)]
        selected_data = selected_data["class"].value_counts().reset_index()
        fig = px.pie(selected_data, values='count',
                     names='class',
                     title=f'Total Success Launches for site {entered_site}')

        return fig


def get_scatter_chart(x_range):

    filtered_df = spacex_data[(spacex_data['Payload Mass (kg)'] >= x_range[0])
                              & (spacex_data['Payload Mass (kg)'] <= x_range[1])]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category',
                     title="Correlation between Payload and Success for all Sites")

    return fig


# Callback decorator
@app.callback([
    Output(component_id='success-pie-chart', component_property='figure'),
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
],
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
# Computation to callback function and return graph
def get_graphs(entered_site, x_range):

    pie_chart_figure = get_pie_chart(entered_site)

    scatter_chart_figure = get_scatter_chart(x_range)

    return [pie_chart_figure, scatter_chart_figure]


# Run the app
app.run_server(debug=True)
