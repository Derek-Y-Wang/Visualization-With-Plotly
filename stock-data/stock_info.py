from alpha_vantage.timeseries import TimeSeries

import pandas as pd
import plotly
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

f = open("api-key.txt", "r")
key = f.read()
f.close()

ticker = "GME"

# Time series output as pandas
ts = TimeSeries(key=key, output_format='pandas')

# Get json object with the intraday data and another with  the call's metadata
data, meta_data = ts.get_intraday(symbol=ticker, interval='1min',
                                  outputsize='compact')

# processing the pandas dataframe because we only want to graph closing price
# and volume
graphed_df = data.copy()
graphed_df = graphed_df[['4. close', '5. volume']]
# graphed_df = graphed_df.transpose()


# Rename columns to easier names
graphed_df.rename(columns={"4. close": "price", "5. volume": "volume"},
                  inplace=True)
graphed_df = graphed_df.reset_index().rename(columns={'index': 'indicator'})
print(graphed_df)

# graphed_df = pd.melt(graphed_df, id_vars=['indicator'], var_name='date', value_name='rate')
# print(graphed_df)
#
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id="ticker",
        options=[{"label": x, "value": x}
                 for x in graphed_df.columns[1:]],
        value=graphed_df.columns[1],
        clearable=False,
        style={'width': "40%", 'padding': '2px'}
    ),
    dcc.Graph(id="time-series-chart", style={'width': '90%'}),
])

@app.callback(
    Output("time-series-chart", "figure"),
    [Input("ticker", "value")])
def display_time_series(ticker):
    fig = px.line(graphed_df, x='date', y=ticker, template='plotly_dark')

    return fig

app.run_server(debug=True)
