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
gtabl_cols = ['SNP', 'phenotype', 'beta_GWAS', 'pval_GWAS', 'FDR_GWAS', 'BON_GWAS']
guser_cols = ['SNP', 'Volume Phenotype', 'GWAS beta', 'GWAS p', 'GWAS FDR(p)', 'GWAS Bonf(p)']

ttabl_cols = ['jti_model', 'phenotype', 'beta_TWAS', 'pval_TWAS', 'FDR_TWAS', 'BON_TWAS']
tuser_cols = ['JTI Gene Model', 'Volume Phenotype', 'TWAS beta', 'TWAS p', 'TWAS FDR(p)', 'TWAS Bonf(p)']

gwas_cols = [{'name': n, 'id': c} for n, c in zip(guser_cols[:-4], gtabl_cols[:-4])]
twas_cols = [{'name': n, 'id': c} for n, c in zip(tuser_cols[:-4], ttabl_cols[:-4])]

sci_kws = {'type': 'numeric', 'format': {'specifier': '.2e'}}
gwas_cols += [{'name': n, 'id': c, **sci_kws} for n, c in zip(guser_cols[-4:], gtabl_cols[-4:])]
twas_cols += [{'name': n, 'id': c, **sci_kws} for n, c in zip(tuser_cols[-4:], ttabl_cols[-4:])]

gwas_data = pd.read_csv(gwas_path, usecols=gtabl_cols)
twas_data = pd.read_csv(twas_path, usecols=ttabl_cols + ['symbol'])

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
genes_list = np.sort(twas_data['symbol'].unique())
gene_input = dcc.Dropdown(genes_list, None, id='gene_input', \
                          multi=False, placeholder='Enter or select a gene...')

## gene header 
gene_name = html.H3('', id='gene_name') 
ens_label = html.H6('', id='ens_label') 

######################################################################################

## create twas/gwas tables
fcols = [f'{stat}_GWAS' for stat in ['beta', 'pval', 'FDR', 'BON']] + \
        [f'{stat}_TWAS' for stat in ['beta', 'pval', 'FDR', 'BON']] 
scols = ['phenotype', 'SNP', 'jti_model']

col_widths = [{'if': {'column_id': c}, 'width': '15%'} for c in fcols] + \
             [{'if': {'column_id': c}, 'width': '20%'} for c in scols]

kws = {'page_current': 0, 'page_size': 10, 'page_action': 'custom', 'page_count': 0, \
       'sort_action': 'custom', 'sort_mode': 'multi', 'sort_by': [], \
       'style_cell':{'textAlign': 'left'}, 'style_cell_conditional': col_widths}

gwas_table = dash_table.DataTable(id='gene_gwas_table', columns=gwas_cols, **kws)
twas_table = dash_table.DataTable(id='gene_twas_table', columns=twas_cols, **kws)

num_gwas_text = html.H5('', id='num_gwas_text')
num_twas_text = html.H5('', id='num_twas_text')
num_biov_text = html.H5('', id='num_biov_text')

######################################################################################

## create biovu table
biovu_kws = {'style_cell':{'textAlign': 'left'}}
biovu_table = dash_table.DataTable(id='biovu_table', columns=biovu_cols, **biovu_kws) 

######################################################################################

## text for JTI SNP counts 
regs = ['DLPFC', 'Ant. Cingulate', 'Amygdala', 'Hippocampus', \
        'Caudate', 'Putamen', 'Nuc. Accumbens', 'Cerebellum']

jti_cols = [{'name': 'Regional JTI Model', 'id': 'jti_reg'}, {'name': '# SNPs', 'id': 'num_snps'}]
jti_table = dash_table.DataTable(id='jti_table', columns=jti_cols, style_cell={'textAlign': 'left'})

######################################################################################

## layout 
kws = {'margin': '10px'} 
layout = dbc.Container([

    dbc.Row([
        dbc.Col([
            dbc.Row(gene_input, style=kws), 
            dbc.Row(gene_name, style=kws), 
            dbc.Row(ens_label, style=kws), 
            dbc.Row(jti_table, style=kws),
            ],
            width=3), 

        dbc.Col([
            dbc.Row(num_twas_text, style=kws),
            dbc.Row(twas_table, style=kws), 
            dbc.Row(num_gwas_text, style=kws),
            dbc.Row(gwas_table, style=kws), 
            dbc.Row(num_biov_text, style=kws),
            dbc.Row(biovu_table, style=kws), 
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

    prevent_initial_call=True
    )

def update_gene_twas_table(gene, page_current, page_size, sort_by): 

    if not gene: return None, None, None, None, None
    df = twas_data.loc[twas_data['symbol'] == gene]

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
           'TWAS: {} results found'.format(df.shape[0]), \
           num_pages, gene, sym2ens[gene] 

## callback: update GWAS table 
@callback(
    [Output('gene_gwas_table', 'data'),
     Output('num_gwas_text', 'children'),
     Output('gene_gwas_table', 'page_count')],

    Input('gene_input', 'value'), 
    Input('gene_gwas_table', 'page_current'),
    Input('gene_gwas_table', 'page_size'),
    Input('gene_gwas_table', 'sort_by'),

    prevent_initial_call=True
    )

def update_gene_gwas_table(gene, page_current, page_size, sort_by): 

    if not gene: return None, None
    snps = gene2snps[gene]
    df = gwas_data.loc[gwas_data['SNP'].isin(snps)]

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
           'GWAS: {} results found'.format(df.shape[0]), \
           num_pages

## callback: update BioVU table 
@callback(
    [Output('biovu_table', 'data'), 
     Output('num_biov_text', 'children')],

    Input('gene_input', 'value'), 
    prevent_initial_call=True
    )

def update_biovu_table(gene): 

    if not gene: return None
    df = biovu_data.loc[biovu_data['sym'] == gene]
    df = df.sort_values(['tissue', 'phename', 'volume'])

    return df.to_dict('records'), \
           'BioVU Shared Genes: {} results found'.format(df.shape[0])

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

