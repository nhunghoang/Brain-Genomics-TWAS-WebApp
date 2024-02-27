'''
Main app script. 

Nhung, Jan 2024
'''

import numpy as np 
import pandas as pd 

import dash
from dash import Dash
from dash import html, dcc 

import dash_bootstrap_components as dbc

## init app 
app = Dash(__name__, use_pages=True, \
           external_stylesheets=[dbc.themes.UNITED], \
           suppress_callback_exceptions=True)

twas_page_path = dash.page_registry['pages.twas_home']['path']
gene_page_path = dash.page_registry['pages.gene_page']['path']

## top navigation bar
navbar = dbc.Nav([
    dbc.NavItem(dbc.NavLink('Neuroimaging TWAS', active=True, href=twas_page_path, style={'color': 'black'})),
    dbc.NavItem(dbc.NavLink('Gene Summaries', href=gene_page_path, style={'color': 'black'})),
    ],
    style={'background-color': '#b6d7a8', 'font-size': '125%'}
)

## app layout 
app.layout = html.Div([navbar, dash.page_container]) 

## main call 
if __name__ == '__main__':
    app.run(debug=True)

