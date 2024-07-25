#!/usr/bin/env python
# coding: utf-8


# In[ ]:


# Dashboard


# In[2]:


import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data from Excel file
excel_path = "/Users/michelemodregger/Desktop/varie/Real Estate/real_estate_data.xlsx"
df_rent = pd.read_excel(excel_path, sheet_name='Rent Data')
df_sale = pd.read_excel(excel_path, sheet_name='Sale Data')

# Preprocess the data
df_rent['Price per Square Meter'] = pd.to_numeric(df_rent['Price per Square Meter'], errors='coerce')
df_sale['Price per Square Meter'] = pd.to_numeric(df_sale['Price per Square Meter'], errors='coerce')

# Calculate aggregate data for each district
rent_agg = df_rent.groupby('District')['Price per Square Meter'].mean().reset_index()
sale_agg = df_sale.groupby('District')['Price per Square Meter'].mean().reset_index()

# Merge rent and sale aggregate data
agg_data = pd.merge(rent_agg, sale_agg, on='District', suffixes=('_Rent', '_Sale'))
agg_data['Yield'] = (agg_data['Price per Square Meter_Rent'] * 12) / agg_data['Price per Square Meter_Sale']
agg_data['Yield'] = (agg_data['Yield'] * 100).round(2).astype(str) + '%'
agg_data['Price per Square Meter_Rent'] = '€' + agg_data['Price per Square Meter_Rent'].apply(lambda x: f'{x:.2f}')
agg_data['Price per Square Meter_Sale'] = '€' + agg_data['Price per Square Meter_Sale'].apply(lambda x: f'{x:.2f}')

# Rename columns for better readability
agg_data.rename(columns={
    'Price per Square Meter_Rent': 'Rent price/sqm',
    'Price per Square Meter_Sale': 'Sale price/sqm'
}, inplace=True)

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Real Estate Dashboard"),
    html.H2("Aggregate Data by District"),
    dcc.Dropdown(
        id='district-dropdown',
        options=[{'label': district, 'value': district} for district in agg_data['District']],
        placeholder="Select a District"
    ),
    html.Div(id='district-summary'),
    html.Div([
        dcc.Graph(id='district-sale-plot', style={'width': '100%'}),
        dcc.Graph(id='district-rent-plot', style={'width': '100%'})
    ], style={'width': '100%'}),
    html.H2("Data Breakdown"),
    html.Div(id='district-detail-table', style={'overflowX': 'auto', 'width': '100%'})  # Adjust table width
])

# Callback to update the summary table and plots
@app.callback(
    [Output('district-summary', 'children'),
     Output('district-sale-plot', 'figure'),
     Output('district-rent-plot', 'figure')],
    [Input('district-dropdown', 'value')]
)
def update_summary(selected_district):
    if selected_district:
        summary = agg_data[agg_data['District'] == selected_district]
        summary_table = html.Table([
            html.Tr([html.Th(col, style={'textAlign': 'center'}) for col in summary.columns]),
            html.Tr([html.Td(summary[col].values[0], style={'textAlign': 'center'}) for col in summary.columns])
        ], style={'width': '100%', 'border-collapse': 'collapse'})  # Full width, no border
        
        detail_rent = df_rent.loc[df_rent['District'] == selected_district].copy()
        detail_sale = df_sale.loc[df_sale['District'] == selected_district].copy()

        detail_rent['Type'] = 'Rent'
        detail_sale['Type'] = 'Sale'

        # Rent plot
        rent_fig = px.scatter(detail_rent, x='Area', y='Price per Square Meter', color='Type',
                             color_discrete_sequence=['blue'],
                             hover_data=['Price', 'Energy Class', 'Parking', 'Balcony/Terrace'])
        
        # Sale plot
        sale_fig = px.scatter(detail_sale, x='Area', y='Price per Square Meter', color='Type',
                             color_discrete_sequence=['red'],
                             hover_data=['Price', 'Energy Class', 'Parking', 'Balcony/Terrace'])

        return summary_table, sale_fig, rent_fig
    else:
        return html.Div(), px.scatter(), px.scatter()

# Callback to update the detailed table for the selected district
@app.callback(
    Output('district-detail-table', 'children'),
    [Input('district-dropdown', 'value')]
)
def update_detail_table(selected_district):
    if selected_district:
        detail_rent = df_rent.loc[df_rent['District'] == selected_district].copy()
        detail_sale = df_sale.loc[df_sale['District'] == selected_district].copy()

        detail_rent['Type'] = 'Rent'
        detail_sale['Type'] = 'Sale'

        detail_data = pd.concat([detail_rent, detail_sale])
        
        # Remove ID and Address columns if they exist
        detail_data = detail_data.drop(columns=['ID', 'Address'], errors='ignore')
        
        # Format columns
        if 'Price per Square Meter' in detail_data.columns:
            detail_data['Price per Square Meter'] = '€' + detail_data['Price per Square Meter'].apply(lambda x: f'{x:.2f}')
        
        if 'Area' in detail_data.columns:
            detail_data['Area'] = detail_data['Area'].apply(lambda x: f'{x:.2f} m²')
        
        # Create table
        detail_table = html.Table([
            html.Tr([html.Th(col, style={'textAlign': 'center'}) for col in detail_data.columns]),
            *[html.Tr([html.Td(detail_data.iloc[i][col], style={'textAlign': 'center'}) for col in detail_data.columns]) for i in range(len(detail_data))]
        ], style={'width': '100%', 'border-collapse': 'collapse'})  # Full width, no border
        
        return detail_table
    else:
        return html.Div()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)


# In[ ]:




