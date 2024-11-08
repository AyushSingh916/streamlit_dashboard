import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import geopandas as gpd

st.set_page_config(
    page_title='Global Disaster Atlas',
    page_icon = './assets/icons/atlas_icon.png',
    layout='wide',
    initial_sidebar_state='collapsed'
)
st.title('Data Preview')

df = pd.read_csv('./assets/dataset/cleaned_data.csv')

st.write(df.head())

# Streamlit layout
st.title("Total Deaths by Country (Filtered by Disaster Type)")

# Dropdown filter for Disaster Type
disaster_type = st.selectbox(
    'Select Disaster Type',
    df['Disaster Type'].unique(),
    index=0  # Default to the first disaster type
)

# Filter the dataframe based on the selected disaster type
filtered_df = df[df['Disaster Type'] == disaster_type]

# Create scatter geo map
fig = px.scatter_geo(
    filtered_df,
    lat="Latitude",
    lon="Longitude",
    size="Total Deaths",
    hover_name="Location",
    hover_data={
        'Country': True,
        'Total Deaths': True,
        'Total Damage (\'000 US$)': True,
        'Latitude': True,
        'Longitude': True,
        'Location': False  # Hide Location in hover_data (handled separately in hovertemplate)
    },
    title=f"Total Deaths by Disaster Location for {disaster_type}",
    color="Total Deaths",
    color_continuous_scale="Reds",
    size_max=50
)

# Update the layout for better aesthetics
fig.update_layout(
    title_font_size=22,
    title_x=0.5,
    title_y=0.95,  # Center the title
    title_font_color='#2c3e50',
    geo=dict(showland=True, landcolor="lightgray"),
    paper_bgcolor='#f7f7f7',
    plot_bgcolor='#f7f7f7',
    font=dict(color='#2c3e50', size=14),
    margin={"r": 0, "t": 50, "l": 0, "b": 0}
)

# Customize hover labels
fig.update_traces(
    marker=dict(line=dict(width=0.5, color='DarkSlateGrey')),
    hovertemplate=(
        "Country: %{customdata[0]}<br>"
        "Total Deaths: %{marker.size:,}<br>"
        "Latitude: %{lat}<br>"
        "Longitude: %{lon}"
    )
)

# Display the map in Streamlit
st.plotly_chart(fig)

col1,col2 = st.columns(2)
fig_line = px.line(
    df,
    x='Start_Date',
    y="Total Damage, Adjusted ('000 US$)",  # Keep the original column name
    color='Disaster Subgroup',
    title="Total Damage Over Time by Disaster Subgroup",
    labels={
        "Total Damage, Adjusted ('000 US$)": "Total Damage (US$)",  # Modify y-axis label
        'Start_Date': 'Date'
    },
    line_shape='linear'  # Ensure smooth lines
)

# Update layout for better visibility
fig_line.update_layout(
    xaxis_title='Date',
    yaxis_title="Total Damage (US$)",  # Change y-axis title
    hovermode='x unified',  # Unified hover for all lines at the same x-axis point
    legend_title_text='Disaster Subgroup',
    template='plotly_white',  # Enhance the visual style
    height=600,  # Set the plot height
)

# Update hover and trace styles
fig_line.update_traces(
    mode='lines+markers',  # Display both lines and markers for better point visibility
    marker=dict(size=4),  # Set marker size
    hovertemplate='<b>Date</b>: %{x}<br><b>Total Damage</b>: %{y:.2f} (\'US$)<br><b>Disaster Subgroup</b>: %{fullData.name}'  # Retain detailed hover with '000 US$'
)

# Show the plot
col1.plotly_chart(fig_line)
df['Start_Date'] = pd.to_datetime(df['Start_Date'])
df_sorted = df.sort_values(by='Start_Date')

# Cumulative sum of Total Deaths by Region
df_sorted['Cumulative_Deaths'] = df_sorted.groupby('Region')['Total Deaths'].cumsum()

# Cumulative Line Chart: Total Deaths by Region Over Time with improved styling
fig_cumulative_deaths = px.line(
    df_sorted,
    x='Start_Date',
    y='Cumulative_Deaths',
    color='Region',
    title="Cumulative Total Deaths by Region Over Time",
    labels={'Cumulative_Deaths': 'Cumulative Total Deaths', 'Start_Date': 'Date'},
    hover_data=['Disaster Type', 'Country'],  # Show additional data on hover
    line_shape='linear'  # Change to 'linear' to avoid jagged lines
)

# Update layout for better visibility
fig_cumulative_deaths.update_layout(
    xaxis_title='Date',
    yaxis_title='Cumulative Total Deaths',
    hovermode='x unified',  # Show hover details for all lines at the same x-axis point
    legend_title_text='Region',
    template='plotly_white',  # Improve visual appearance with white background
    height=600,  # Increase plot height
)

# Improve hover and trace visibility
fig_cumulative_deaths.update_traces(
    mode='lines+markers',  # Show lines with markers to improve point visibility
    marker=dict(size=4),  # Increase marker size for better readability
    hovertemplate='<b>Date</b>: %{x}<br><b>Cumulative Deaths</b>: %{y}<br><b>Region</b>: %{fullData.name}<br><b>Disaster Type</b>: %{customdata[0]}<br><b>Country</b>: %{customdata[1]}'  # Custom hover data
)

# Show the plot
col2.plotly_chart(fig_cumulative_deaths)

all_countries = df['Country'].unique()

# Create the dynamic bar chart
fig_bar = px.bar(
    df,
    x='Disaster Type',
    y='Total Deaths',
    color='Country',
    title="Total Deaths by Disaster Type and Country",
    labels={'Total Deaths': 'Total Deaths', 'Disaster Type': 'Disaster Type'},
    category_orders={'Country': all_countries}  # Ensure all countries appear in the filter
)

col1.plotly_chart(fig_bar)

# Scatter Plot: Total Deaths vs. Total Damage (Adjusted) by Disaster Subgroup
st.title('Disaster Magnitude vs Total Death and Destruction')
fig_scatter = px.scatter(
    df,
    x="Total Damage, Adjusted ('000 US$)",
    y='Total Deaths',
    color='Disaster Subgroup',
    size='Total Deaths',  # Bubble size based on Total Deaths
    hover_data=['Country', 'Disaster Type'],  # Add more details to the hover tooltip
    title="Scatter Plot: Total Deaths vs. Total Damage by Disaster Subgroup",
    labels={
        "Total Damage, Adjusted ('000 US$)": "Total Damage, Adjusted ('000 US$)",
        "Total Deaths": "Total Deaths"
    },
    template='plotly_white'
)

# Improve layout
fig_scatter.update_layout(
    xaxis_title="Total Damage, Adjusted (US$)",
    yaxis_title="Total Deaths",
    height=600,
    legend_title="Disaster Subgroup"
)

# Display the initial scatter plot
col2.plotly_chart(fig_scatter)
# Function to remove outliers using the IQR method
all_countries = df['Country'].unique()



# Function to remove outliers using the IQR method
# Function to remove outliers using the IQR method
def remove_outliers(df, column):
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]

# List of specific disaster types for dropdown menu
disaster_types = ['Earthquake', 'Flood', 'Storm']

# Dropdown menu for selecting the disaster type
selected_disaster_type = st.selectbox("Select Disaster Type", disaster_types)

# Button to confirm the selection
if st.button("Show Plot"):
    # Filter the dataframe for the selected disaster type
    df_filtered = df[df['Disaster Type'] == selected_disaster_type]

    # Remove outliers from Magnitude and Total Deaths
    df_filtered = remove_outliers(df_filtered, 'Magnitude')
    df_filtered = remove_outliers(df_filtered, 'Total Deaths')

    # Find the maximum values for Magnitude and Total Deaths to adjust the axes dynamically
    max_magnitude = df_filtered['Magnitude'].max()
    max_total_deaths = df_filtered['Total Deaths'].max()

    # Create the scatter plot for the selected disaster type
    fig_magnitude_deaths = px.scatter(
        df_filtered,
        x='Magnitude',
        y='Total Deaths',
        color='Country',  # Differentiate points by country
        size='Total Damage (\'000 US$)',
        title=f"Magnitude vs Total Deaths for {selected_disaster_type}",
        labels={'Magnitude': 'Disaster Magnitude', 'Total Deaths': 'Total Deaths'},
        hover_data=['Country', 'Region']
    )

    # Update layout for better readability and dynamic axis range
    fig_magnitude_deaths.update_layout(
        xaxis_title='Disaster Magnitude',
        yaxis_title='Total Deaths',
        xaxis=dict(range=[0, max_magnitude + 1]),  # Adjust x-axis range dynamically
        yaxis=dict(range=[0, max_total_deaths + (0.1 * max_total_deaths)]),  # Adjust y-axis range dynamically
        template='plotly_white',
        height=600,
    )

    # Show the plot for the selected disaster type
    st.plotly_chart(fig_magnitude_deaths)
## Heatmap

# Create a pivot table with counts of each Disaster Type per Subregion
df_pivot = df.groupby(['Subregion', 'Disaster Type']).size().unstack(fill_value=0)

# Calculate total counts for each subregion
subregion_counts = df_pivot.sum(axis=1)

# Set a threshold for minimum number of disasters
threshold = 15  # Adjust this value as needed

# Filter out subregions with total counts below the threshold
df_pivot_filtered = df_pivot.loc[subregion_counts[subregion_counts >= threshold].index]

# Calculate total counts for each disaster type after filtering subregions
total_counts = df_pivot_filtered.sum(axis=0)

# Filter out disaster types with counts below the threshold
df_pivot_filtered = df_pivot_filtered.loc[:, total_counts[total_counts > threshold].index]

# Create the heatmap with improved aesthetics
fig_heatmap = px.imshow(
    df_pivot_filtered,
    labels={'color': 'Disaster Count'},
    title='Disaster Frequency by Subregion and Type (Filtered)',
    color_continuous_scale='Viridis',
    text_auto=True  # Show the count on the heatmap
)

# Update layout for better appearance
fig_heatmap.update_layout(
    title_font_size=24,  # Title font size
    xaxis_title='Disaster Type',  # X-axis title
    yaxis_title='Subregion',  # Y-axis title
    xaxis_tickangle=-45,  # Angle x-axis ticks for better readability
    yaxis_autorange='reversed',  # Reverse the y-axis to have the first subregion at the top
    coloraxis_colorbar=dict(
        title='Disaster Count',  # Title for the color bar
        titlefont=dict(size=14),  # Color bar title font size
        tickfont=dict(size=12)  # Color bar tick font size
    ),
    width=1100,  # Increase width of the heatmap
    height=800   # Increase height of the heatmap
)

# Show the enhanced heatmap
st.plotly_chart(fig_heatmap)

