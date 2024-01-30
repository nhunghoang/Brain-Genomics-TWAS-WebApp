'''
Home page w/ interactive TWAS table. 

Nhung, Jan 2024
'''

import numpy as np 
import pandas as pd 
import os

import dash
from dash import Dash, callback, Input, Output
from dash import html, dcc
from dash import dash_table

import dash_bootstrap_components as dbc

###################################################################

## register this page 
dash.register_page(__name__, name='Brain Genomics TWAS', path='/')

###################################################################

## load TWAS data 
tabl_cols = ['phenotype', 'jti_model', 'symbol', 'beta_TWAS', 'pval_TWAS', 'FDR_TWAS', 'BON_TWAS']
user_cols = ['Volume Phenotype', 'JTI Gene Model', 'Gene Symbol', 'Ensembl ID', \
             'TWAS beta', 'TWAS p', 'TWAS FDR(p)', 'TWAS Bonf(p)']

twas_cols = [{'name': n, 'id': c} \
              for n, c in zip(user_cols[:-4], tabl_cols[:-4])]

sci_kws = {'type': 'numeric', 'format': {'specifier': '.2e'}}
twas_cols += [{'name': n, 'id': c, **sci_kws} \
               for n, c in zip(user_cols[-4:], tabl_cols[-4:])]

twas_path = os.getcwd() + '/input_data/twas_ukb_volume.csv' 
twas_data = pd.read_csv(twas_path, usecols=tabl_cols) 

## create TWAS table
page_nrow = 50
num_pages = int(twas_data.shape[0] / page_nrow) + 1 
twas_table = dash_table.DataTable(id='twas_table',
                                  columns=twas_cols,

                                  page_current=0,
                                  page_size=page_nrow,
                                  page_action='custom',
                                  page_count=num_pages,

                                  sort_action='custom',
                                  sort_mode='multi',
                                  sort_by=[],
                                  )

######################################################################################

## dropdown menus for filter options
iregs = ['DLPFC', 'Ant. Cingulate', 'Amygdala', 'Hippocampus', \
         'Caudate', 'Putamen', 'Nuc. Accumbens', 'Cerebellum']
genes = np.sort(twas_data['symbol'].unique())
pvals = {'pvalue': 'nominal p', 'FDR': 'FDR(p)', 'BON': 'Bonf(p)'}

phen_menu = dcc.Dropdown(iregs, None, id='phen_menu', multi=True)
gmod_menu = dcc.Dropdown(iregs, None, id='gmod_menu', multi=True)
gene_menu = dcc.Dropdown(genes, None, id='gene_menu', multi=True)
pval_menu = dcc.Dropdown(pvals, None, id='pval_menu', multi=False)

## user input for pval filter
pval_input = dcc.Input(id='pval_itxt', type='number', min=0, max=1,
                       debounce=True, style={'width': '100%'})

## various text
style_kws = {'display': 'flex', 'align-items': 'center'}
main_text = html.H5('TWAS Table Filters', style=style_kws)
phen_text = html.H6('Regional Volumes:', style=style_kws)
gmod_text = html.H6('Regional JTI Gene Models:', style=style_kws)
gene_text = html.H6('Gene Symbols:', style=style_kws)
pval_txt0 = html.H6('p-value cut-off:', style=style_kws)
pval_txt1 = html.P('<', style=style_kws)

num_res_txt = html.P('', id='num_results_txt', style=style_kws)

######################################################################################

## layout 
kws = {'margin': '10px'} 
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Row(main_text, style=kws),
            dbc.Row(num_res_txt, style=kws),

            dbc.Row(phen_text, style=kws),
            dbc.Row(phen_menu, style=kws),

            dbc.Row(gmod_text, style=kws),
            dbc.Row(gmod_menu, style=kws),

            dbc.Row(gene_text, style=kws),
            dbc.Row(gene_menu, style=kws),

            dbc.Row(pval_txt0, style=kws),
            dbc.Row([
                dbc.Col(pval_menu, width=6),
                dbc.Col(pval_txt1, width=1),
                dbc.Col(pval_input, width=5),
                ],
                style=kws),
            ],
            width=3),

        dbc.Col([
            dbc.Row(twas_table, style=kws),
            ],
            width=9),
        ]),
    ],
    fluid=True,
)

######################################################################################

## callbacks 
@callback(
    [Output('twas_table', 'data'),
     Output('twas_table', 'page_count'),
     Output('num_results_txt', 'children')],

    Input('twas_table', 'page_current'),
    Input('twas_table', 'page_size'),
    Input('twas_table', 'sort_by'),

    Input('phen_menu', 'value'),
    Input('gmod_menu', 'value'),
    Input('gene_menu', 'value'),
    Input('pval_menu', 'value'),
    Input('pval_itxt', 'value'),

    )

def update_twas_table(page_current, page_size, sort_by, \
                      phen_filter, gmod_filter, gene_filter, \
                      pval_filter, pval_input):

    df = twas_data

    ## table filters (logical and)
    mask = np.ones(df.shape[0], dtype=bool)
    if phen_filter:
        mask = np.logical_and(mask, df['phenotype'].isin(phen_filter))
    if gmod_filter:
        mask = np.logical_and(mask, df['jti_model'].isin(gmod_filter))
    if gene_filter:
        mask = np.logical_and(mask, df['symbol'].isin(gene_filter))

    if pval_filter and pval_input:
        mask = np.logical_and(mask, df[pval_filter] < pval_input)

    df = df.loc[mask]
    total_rows = df.shape[0]
    total_rows_text = '{} results found'.format(total_rows)
    num_pages = int(total_rows / page_size) + 1


    ## sorting
    if len(sort_by):
        cols = [col['column_id'] for col in sort_by]
        ascs = [col['direction'] == 'asc' for col in sort_by]
        df = df.sort_values(cols, ascending=ascs)

    ## paging
    top = page_current * page_size
    bot = (page_current + 1) * page_size

    return df.iloc[top:bot].to_dict('records'), \
           num_pages, total_rows_text



