#==============================================================================#
#                                                                              #
#    Title: Flights Dashboard                                                  #
#    Purpose: Interactive Dashboard for Analysing Flight Patterns              #
#    Author: chrimaho                                                          #
#    Created: 07/Aug/2021                                                      #
#                                                                              #
#==============================================================================#




#------------------------------------------------------------------------------#
#                                                                              #
#    Setup                                                                  ####
#                                                                              #
#------------------------------------------------------------------------------#


# Global Imports ----
import streamlit as st
import pandas as pd
import pydeck as pdk
from datetime import date, datetime
import os
import base64

# Constants ----
REPO_NAME = "FLIGHTSDASHBOARD"

# Ensure the directory is correct... every time. ---
for _ in range(5):
    if not os.path.basename(os.getcwd()).lower() == REPO_NAME.lower():
        os.chdir("..")
    else:
        break




#------------------------------------------------------------------------------#
#                                                                              #
#    Functions                                                              ####
#                                                                              #
#------------------------------------------------------------------------------#

def load_data(path:str):
    return pd.read_csv(path, header=0)

@st.cache
def load_flights_data(path:str):
    df = load_data(path)
    df['firstseen'] = pd.to_datetime(df['firstseen']).dt.strftime('%Y-%m-%d')
    return df

@st.cache
def load_covid_data(path:str):
    df = load_data(path)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
    return df

# @st.cache
def download_csv(data:pd.DataFrame):
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    lnk = f'<a href="data:file/csv;base64,{b64}" download="flights.csv">Download CSV</a>'
    st.markdown(lnk, unsafe_allow_html=True)


#------------------------------------------------------------------------------#
#                                                                              #
#    Main                                                                   ####
#                                                                              #
#------------------------------------------------------------------------------#



#------------------------------------------------------------------------------#
# Get Data                                                                  ####
#------------------------------------------------------------------------------#


# Load the flights data filter by date variable
flightDF = load_flights_data("./data/external/flights-jan-mar-2020.csv")

# Load the COVID-19 data and filter by date variable
covidDF = load_covid_data("./data/external/covid.csv")



#------------------------------------------------------------------------------#
# Side Bar                                                                  ####
#------------------------------------------------------------------------------#

sb = st.sidebar
sb.header("Data Sources")
sb.write("**Analysis provided from Public data.**")
sb.write("Flights data from:\nhttps://zenodo.org/record/3737102")
sb.write("Covid data from:\nhttps://ourworldindata.org/coronavirus")
sb.subheader("Future")
sb.write("Imagine the benefit we could add by analysing our own data.")



#------------------------------------------------------------------------------#
# Page Header Parts                                                         ####
#------------------------------------------------------------------------------#


# Title
st.title("Analysis of Flight Patterns")

# Subtitle
st.write("As affected by Covid in early 2020")

# Subheader
st.subheader("Select Date")

# Date
date = st.slider \
    ( " "
    , value=date.fromisoformat("2020-01-01")
    , format="DD/MMM/YY"
    , min_value=date.fromisoformat("2020-01-01")
    , max_value=date.fromisoformat(flightDF["firstseen"].max())
    )


# Subheader
st.subheader("Interactive Map")


# Subheader
st.markdown(unsafe_allow_html=True, body=
"""
The below Map has the following features:

- The <span style="color: rgba(240, 100, 0, 40)">**orange**</span> colour indicates the DEPARTURE airport.
- The <span style="color: rgba(0, 200, 0, 100)">**green**</span> colour indicates the DESTINATION airport.
- The <span style="color: red">**red**</span> colour indicates countries with COVID hotspots, and<br>
the size of the circle indicates the amount of cases.
""")




#------------------------------------------------------------------------------#
# Filter Data                                                               ####
#------------------------------------------------------------------------------#

# Flights
flightDF = flightDF[flightDF['firstseen'] == date.isoformat()]

# Covid

covidDF = covidDF[covidDF['date'] == date.isoformat()]



#------------------------------------------------------------------------------#
# Set Visual                                                                ####
#------------------------------------------------------------------------------#


# Set viewport for the deckgl map
view = pdk.ViewState(latitude=0, longitude=0, zoom=0.2,)

# Set colours for the origin and destination ends of the arc
DESTINATION_COLOUR = [0, 255, 0, 40]
ORIGIN_COLOUR = [240, 100, 0, 40]

# Create the arc layer
arcLayer = pdk.Layer \
    ( "ArcLayer"
    , data=flightDF
    , get_width=2
    , get_source_position=['origin_lng', 'origin_lat']
    , get_target_position=['destination_lng', 'destination_lat']
    , get_tilt=15
    , get_source_color=ORIGIN_COLOUR
    , get_target_color=DESTINATION_COLOUR
    , pickable=True
    , auto_highlight=True
    )

# Configure the tooltip
TOOLTIP_TEXT = {"html": "{number} from {origin_country} to {destination_country}"}

# Create the scatter plot layer
covidLayer = pdk.Layer \
    ( "ScatterplotLayer"
    , data=covidDF
    , pickable=False
    , opacity=0.8
    , stroked=True
    , filled=True
    , radius_scale=5
    , radius_min_pixels=1
    , radius_max_pixels=1000
    , line_width_min_pixels=1
    , get_position=["Longitude", "Latitude"]
    , get_radius="total_cases"
    , get_fill_color=[255,0,0]
    , get_line_color=[255,0,0]
    )




# Render the map in the Streamlit app as a Pydeck chart 
map = st.pydeck_chart \
    ( pdk.Deck \
        ( layers=[covidLayer,arcLayer]
        , initial_view_state=view
        , map_style="mapbox://styles/mapbox/dark-v9"
        , tooltip=TOOLTIP_TEXT
        )
    )

# Subheader
st.subheader("To see the raw data, check:")

# Add Flights data
if st.checkbox("See Flights Data"):
    download_csv(flightDF)
    st.write('Flights on %s' % date.strftime("%d/%b/%y"))
    st.write(flightDF.head())

# Add Covid data
if st.checkbox("See Covid data"):
    download_csv(covidDF)
    st.write('COVID-19 data on %s' % date.strftime("%d/%b/%y"))
    st.write(covidDF.head())