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
dash.register_page(__name__, name='Gene Summary')

###################################################################

## paths
main_path = os.getcwd() + '/input_data/'

mapp_path = main_path + 'jti_gene2snp.csv'
map2_path = main_path + 'jti_ens2gene.csv'

gwas_path = main_path + 'gwas_ukb_volume.csv'
twas_path = main_path + 'twas_ukb_volume.csv'

biov_path = main_path + 'biovu_ukb_volume.csv'

###################################################################

## load gene-to-snp map 
mapp = pd.read_csv(mapp_path)
gene2snps = mapp.groupby('symbol')['snp'].apply(list)
jti2snps = mapp.groupby(['symbol', 'region'])['snp'].count()

## load gene symbol-to-ensembl map
sym2ens = pd.read_csv(map2_path, index_col='sym').to_dict()['ens']

###################################################################

## load twas/gwas data
gtabl_cols = ['SNP', 'Predicted Volume', 'GWAS beta', 'GWAS p', 'GWAS p(FDR)', 'GWAS p(Bonf)']
ttabl_cols = ['gr-Expression Site', 'Predicted Volume', 'TWAS beta', 'TWAS p', 'TWAS p(FDR)', 'TWAS p(Bonf)']

gwas_cols = [{'name': c, 'id': c} for c in gtabl_cols[:-4]]
twas_cols = [{'name': c, 'id': c} for c in ttabl_cols[:-4]]

sci_kws = {'type': 'numeric', 'format': {'specifier': '.2e'}}
gwas_cols += [{'name': c, 'id': c, **sci_kws} for c in gtabl_cols[-4:]]
twas_cols += [{'name': c, 'id': c, **sci_kws} for c in ttabl_cols[-4:]]

gwas_data = pd.read_csv(gwas_path, usecols=gtabl_cols)
twas_data = pd.read_csv(twas_path, usecols=ttabl_cols + ['Gene'])

###################################################################

## load biovu data 
btabl_cols = ['tissue', 'phename', 'FDR_PDX', 'volume', 'FDR_UKB']
buser_cols = ['JTI Gene Model', 'BioVU Phenotype', 'TWAS FDR(p)', 'Volume Phenotype', 'TWAS FDR(p)']

biovu_cols = [{'name': n, 'id': c} for n, c in zip(buser_cols, btabl_cols)]
biovu_cols[-3] = {'name': buser_cols[-3], 'id': btabl_cols[-3], **sci_kws}
biovu_cols[-1] = {'name': buser_cols[-1], 'id': btabl_cols[-1], **sci_kws}

biovu_data = pd.read_csv(biov_path, usecols=btabl_cols + ['sym', 'phecode'])

def rename(phecode, phename): return f'{phecode}: {phename}'
biovu_data['phename'] = biovu_data.apply(lambda x: rename(x['phecode'], x['phename']), axis=1)

###################################################################

## gene prompt 
genes_list = np.sort(twas_data['Gene'].unique())
gene_input = dcc.Dropdown(genes_list, None, id='gene_input', \
                          multi=False, placeholder='Enter or select a gene...')

## gene header 
gene_name = html.H3('', id='gene_name') 
ens_label = html.H6('', id='ens_label') 

######################################################################################

## create twas/gwas tables
fcols = [f'GWAS {stat}' for stat in ['beta', 'p', 'p(FDR)', 'p(BON)']] + \
        [f'TWAS {stat}' for stat in ['beta', 'p', 'p(FDR)', 'p(BON)']] 
scols = ['Predicted Volume', 'SNP', 'gr-Expression Site']

col_widths = [{'if': {'column_id': c}, 'width': '15%'} for c in fcols] + \
             [{'if': {'column_id': c}, 'width': '20%'} for c in scols]

kws = {'page_current': 0, 'page_size': 10, 'page_action': 'custom', 'page_count': 0, \
       'sort_action': 'custom', 'sort_mode': 'multi', 'sort_by': [], \
       'style_cell':{'textAlign': 'left'}, 'style_cell_conditional': col_widths}

gwas_table = dash_table.DataTable(id='gene_gwas_table', columns=gwas_cols, **kws)
twas_table = dash_table.DataTable(id='gene_twas_table', columns=twas_cols, **kws)

num_gwas_text = html.H5('Neuroimaging GWAS', id='num_gwas_text')
num_twas_text = html.H5('Neuroimaging TWAS', id='num_twas_text')
num_biov_text = html.H5('Clinical TWAS', id='num_biov_text')

######################################################################################

## create biovu table
biovu_kws = {'style_cell':{'textAlign': 'left'}}
biovu_table = dash_table.DataTable(id='biovu_table', columns=biovu_cols, **biovu_kws) 

######################################################################################

## filter options 
skws = {'display': 'flex', 'align-items': 'center'}
twas_pval_text = html.H6('TWAS Signif:', style=skws) 
gwas_pval_text = html.H6('GWAS Signif:', style=skws) 

twas_pvals = {'TWAS p': 'p <', 'TWAS p(FDR)': 'p(FDR) <', 'TWAS p(Bonf)': 'p(Bonf) <'}
gwas_pvals = {'GWAS p': 'p <', 'GWAS p(FDR)': 'p(FDR) <', 'GWAS p(Bonf)': 'p(Bonf) <'}

mkws = {'multi': False, 'clearable': False}
twas_pval_menu = dcc.Dropdown(twas_pvals, 'TWAS p', id='twas_pval_menu', **mkws)
gwas_pval_menu = dcc.Dropdown(gwas_pvals, 'GWAS p', id='gwas_pval_menu', **mkws)

ikws = {'type': 'number', 'min': 0, 'max': 1, 'debounce': True, 'style': {'width': '100%'}} 
twas_pval_input = dcc.Input(id='twas_pval_input', value=1, **ikws)
gwas_pval_input = dcc.Input(id='gwas_pval_input', value=1, **ikws)

######################################################################################

## text for JTI SNP counts 
regs = ['DLPFC', 'Ant. Cingulate', 'Amygdala', 'Hippocampus', \
        'Caudate', 'Putamen', 'Nuc. Accumbens', 'Cerebellum']

jti_cols = [{'name': 'gr-Expression Site', 'id': 'jti_reg'}, {'name': '# SNPs', 'id': 'num_snps'}]
jti_table = dash_table.DataTable(id='jti_table', columns=jti_cols, style_cell={'textAlign': 'left'})

######################################################################################

## layout 
kws = {'margin': '10px'} 
kws1 = {'margin': '10px 0px 20px 10px', \
        'background-color': '#C0C0C0', \
        'padding': '10px 6px 6px 6px', 'border-radius': '5px'}

layout = dbc.Container([

    dbc.Row([
        dbc.Col([

            dbc.Row([
                dbc.Row(gene_input, style={'margin': '5px 5px 20px 0px'}), 

                dbc.Row([
                    dbc.Col(gwas_pval_text, width=3),
                    dbc.Col(gwas_pval_menu, width=5), 
                    dbc.Col(gwas_pval_input, width=4), 
                    ], 
                    align='center', style={'margin': '5px 5px 10px 0px'}), 

                dbc.Row([
                    dbc.Col(twas_pval_text, width=3),
                    dbc.Col(twas_pval_menu, width=5), 
                    dbc.Col(twas_pval_input, width=4), 
                    ], 
                    align='center', style={'margin': '5px 5px 10px 0px'}), 

                ], 
                align='center', style=kws1),

            dbc.Row([
                dbc.Col(gene_name, width='auto'), 
                dbc.Col(ens_label, width='auto'), 
                ], 
                align='center', style={'margin': '10px 0px 10px 10px'}), 

            dbc.Row(jti_table, style={'margin': '10px 0px 10px 10px'}),
            ],
            width=3), 

        dbc.Col([
            dbc.Row(num_gwas_text, style={'margin': '10px 10px 0px 0px'}),
            dbc.Row(gwas_table, style={'margin': '0px 10px 20px 0px'}), 
            dbc.Row(num_twas_text, style={'margin': '10px 10px 0px 0px'}),
            dbc.Row(twas_table, style={'margin': '0px 10px 20px 0px'}), 
            dbc.Row(num_biov_text, style={'margin': '10px 10px 0px 0px'}),
            dbc.Row(biovu_table, style={'margin': '0px 10px 20px 0px'}), 
            ], 
            width=9), 
        ]), 
    ], 
    fluid=True, 
)

######################################################################################

## callback: update TWAS table 
@callback(
    [Output('gene_twas_table', 'data'),
     Output('num_twas_text', 'children'),
     Output('gene_twas_table', 'page_count'),
     Output('gene_name', 'children'),
     Output('ens_label', 'children')], 

    Input('gene_input', 'value'), 
    Input('gene_twas_table', 'page_current'),
    Input('gene_twas_table', 'page_size'),
    Input('gene_twas_table', 'sort_by'),

    Input('twas_pval_menu', 'value'),
    Input('twas_pval_input', 'value'),

    prevent_initial_call=True
    )

def update_gene_twas_table(gene, page_current, page_size, sort_by, pval_type, pval_text): 

    if not gene: return None, None, None, None, None
    df = twas_data.loc[twas_data['Gene'] == gene]

    ## filters 
    if pval_type: 
        df = df.loc[df[pval_type] < pval_text] 

    num_pages = int(df.shape[0] / page_size) + 1

    ## sorting
    if len(sort_by):
        cols = [col['column_id'] for col in sort_by]
        ascs = [col['direction'] == 'asc' for col in sort_by]
        df = df.sort_values(cols, ascending=ascs)

    ## paging
    top = page_current * page_size
    bot = (page_current + 1) * page_size
    return df.iloc[top:bot].to_dict('records'), \
           'Neuroimaging TWAS: {} results'.format(df.shape[0]), \
           num_pages, gene, f'({sym2ens[gene]})' 

## callback: update GWAS table 
@callback(
    [Output('gene_gwas_table', 'data'),
     Output('num_gwas_text', 'children'),
     Output('gene_gwas_table', 'page_count')],

    Input('gene_input', 'value'), 
    Input('gene_gwas_table', 'page_current'),
    Input('gene_gwas_table', 'page_size'),
    Input('gene_gwas_table', 'sort_by'),

    Input('gwas_pval_menu', 'value'),
    Input('gwas_pval_input', 'value'),

    prevent_initial_call=True
    )

def update_gene_gwas_table(gene, page_current, page_size, sort_by, pval_type, pval_text): 

    if not gene: return None, None, None
    snps = gene2snps[gene]
    df = gwas_data.loc[gwas_data['SNP'].isin(snps)]

    ## filters 
    if pval_type: 
        df = df.loc[df[pval_type] < pval_text] 

    num_pages = int(df.shape[0] / page_size) + 1

    ## sorting
    if len(sort_by):
        cols = [col['column_id'] for col in sort_by]
        ascs = [col['direction'] == 'asc' for col in sort_by]
        df = df.sort_values(cols, ascending=ascs)

    ## paging
    top = page_current * page_size
    bot = (page_current + 1) * page_size
    return df.iloc[top:bot].to_dict('records'), \
           'Neuroimaging GWAS: {} results'.format(df.shape[0]), \
           num_pages

## callback: update BioVU table 
@callback(
    [Output('biovu_table', 'data'), 
     Output('num_biov_text', 'children')],

    Input('gene_input', 'value'), 
    prevent_initial_call=True
    )

def update_biovu_table(gene): 

    if not gene: return None, None
    df = biovu_data.loc[biovu_data['sym'] == gene]
    df = df.sort_values(['tissue', 'phename', 'volume'])

    return df.to_dict('records'), \
           'Clinical TWAS: {} results'.format(df.shape[0])

## callback: report number of JTI snps 
@callback(
    Output('jti_table', 'data'), 
    Input('gene_input', 'value'), 
    prevent_initial_call=True
    ) 

def report_jti_counts(gene): 

    if not gene: return None
    data = []
    for reg in regs: 
        try: num = jti2snps[(gene, reg)]
        except KeyError: num = 0 
        data.append({'jti_reg': reg, 'num_snps': num})

    return data

