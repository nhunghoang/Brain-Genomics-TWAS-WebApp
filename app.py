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
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Summaries by Gene', href=gene_page_path)),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem('More', header=True),
                dbc.DropdownMenuItem('Preprint', href="#"),
                dbc.DropdownMenuItem('GitHub', href="#"),
            ],
            nav=True,
            in_navbar=True,
            label='More',
        ),
    ],
    brand='Brain Genomics',
    brand_href=twas_page_path,
    color='primary',
    dark=True,
)

## app layout 
app.layout = html.Div([navbar, dash.page_container]) 

## main call 
if __name__ == '__main__':
    app.run(debug=True)

