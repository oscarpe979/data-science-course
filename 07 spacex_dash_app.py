# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Function to get all launch sites and turn them into a list for the dropdown menue
def get_launch_sites_dropdown_list():
    #Initialize the dropdown list with the default value
    dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
    launch_sites_df = spacex_df.groupby('Launch Site').sum().reset_index()
    for i, launch_site in launch_sites_df.iterrows():
        name = launch_site['Launch Site']
        dictionary = {'label': name, 'value': name}
        dropdown_options.append(dictionary)

    return dropdown_options

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',   options=get_launch_sites_dropdown_list(),
                                                                            value='ALL',
                                                                            placeholder='Select a Launch Site here', 
                                                                            searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={ 0: '0',
                                                        1000: '1000',
                                                        2000: '2000',
                                                        3000: '3000',
                                                        4000: '4000',
                                                        5000: '5000',
                                                        6000: '6000',
                                                        7000: '7000',
                                                        8000: '8000',
                                                        9000: '9000',
                                                        10000: '10000'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data_all = spacex_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(data_all, values='class', 
        names='Launch Site', 
        title='All Launch Sites Success Rate')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        data_site = filtered_site_df.groupby('class')['class'].size().reset_index(name='Count')
        data_site.replace(0, 'Failure', inplace=True)
        data_site.replace(1, 'Success', inplace=True)
        fig = px.pie(data_site, values='Count', 
        names='class', 
        title=f'{entered_site} Sucess Rate')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), Input(component_id="payload-slider", component_property="value")])

def get_scatter_chart(entered_site, payload_range):
    if entered_site == 'ALL':        
        data = spacex_df[spacex_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
        fig = px.scatter(data, x='Payload Mass (kg)', 
        y='class', 
        color="Booster Version Category",
        title='Correlation between Payload and Success for All Sites')
        return fig
    else:
        # return the outcomes piechart for a selected site
        filtered_site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        data_site = filtered_site_df[filtered_site_df['Payload Mass (kg)'].between(payload_range[0], payload_range[1])]
        
        fig = px.scatter(data_site, x='Payload Mass (kg)', 
        y='class', 
        color="Booster Version Category",
        title=f'Correlation between Payload and Success for {entered_site}')
        return fig        

# Run the app
if __name__ == '__main__':
    app.run_server()
