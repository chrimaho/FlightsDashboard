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
from datetime import date
import os, sys, base64

# Constants ----
REPO_NAME = "FLIGHTSDASHBOARD"

# Ensure the directory is correct... every time. ---
for _ in range(5):
    if not os.path.basename(os.getcwd()).lower() == REPO_NAME.lower():
        os.chdir("..")
    else:
        break


# Ensure the current directory is in the system path. ---
if not os.path.abspath(".") in sys.path: sys.path.append(os.path.abspath("."))




#------------------------------------------------------------------------------#
#                                                                              #
#    Setup                                                                  ####
#                                                                              #
#------------------------------------------------------------------------------#


# Wide page
st.set_page_config \
    ( layout="wide"
    )




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

@st.cache
def load_cars_data(path:str):
    df = load_data(path)
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

# 2014 locations of car accidents in the UK
carsDF = load_cars_data("./data/external/car-accidents.csv")



#------------------------------------------------------------------------------#
# Side Bar                                                                  ####
#------------------------------------------------------------------------------#

sb = st.sidebar
sb.markdown(unsafe_allow_html=True, body=
"""
### Data Sources
Analysis provided from Public data.<br>
*Flights*:\n[Zenodo.org](https://zenodo.org/record/3737102)<br>
*Covid*:\n[OurWorldInData.org](https://ourworldindata.org/coronavirus)<br>
*Uber*:\n[GitHub/Uber-common](https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv)<br>
"""
)
sb.markdown(unsafe_allow_html=True, body=
"""
### Future
Imagine the benefit we could add by analysing **our own** data.
"""
)
sb.markdown(unsafe_allow_html=True, body=
"""
### Source Code
[GitHub](https://github.com/chrimaho/FlightsDashboard)<br>
[StreamLit](https://share.streamlit.io/chrimaho/flightsdashboard/main/src/dashboard/db.py)
""")
sb.markdown(unsafe_allow_html=True, body=
"""
### Author
[Chris Mahoney](https://www.chrimaho.com)
""")



#------------------------------------------------------------------------------#
#                                                                              #
#    Flights Data                                                           ####
#                                                                              #
#------------------------------------------------------------------------------#


#------------------------------------------------------------------------------#
# Page Header Parts                                                         ####
#------------------------------------------------------------------------------#


# Title
st.title("Analysis of Flight Patterns")
st.write("*As affected by Covid in early 2020*")

st.markdown(unsafe_allow_html=True, body=
"""
The following analysis shows the number of flights coming in and out of Australia.

It is easy to see how all throughout January & February, there was a healthy amount of flights coming and going out of Australia. Primarily to the key areas of APAC Middle East, Europe & America.

However, as COVID hit us at the end of March, you will see how quickly the COVID hotspots increased, and you can see how dramatically the flights density dropped off.

This is knowledge that we all know and understand. This visualisation confirms our pre-existing belief of what happened during this time. However, the value of this visual is how interactive it is, and how easily one can navigate around to get a thorough understanding of the situation, in a very short amount of time.
"""
)

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
the SIZE of the circle indicates the amount of cases.
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
view = pdk.ViewState(latitude=0, longitude=0, zoom=0.2)

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

# Protips
st.markdown(unsafe_allow_html=True, body=
"""
**ProTips:**

1. <img src="https://icons-for-free.com/iconfiles/png/512/move-1321215623357277485.png" width=30></img> To pan : `click` & drag
2. <img src="https://icons-for-free.com/iconfiles/png/512/zoom+icon-1320166878528919604.png" width=30></img>To zoom: `scroll` up & down
3. <img src="https://icons-for-free.com/iconfiles/png/512/rotate+icon-1320166903129623074.png" width=30></img> To rotate: `ctrl`+`click` & drag
"""
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
    

# Break
st.write("---")


#------------------------------------------------------------------------------#
#                                                                              #
#    Land                                                                   ####
#                                                                              #
#------------------------------------------------------------------------------#



#------------------------------------------------------------------------------#
# Header                                                                    ####
#------------------------------------------------------------------------------#

# Title
st.title("Analysis of Uber Accidents")
st.write("*For data in England*")

# Analysis
st.markdown(unsafe_allow_html=True, body=
"""
The following analysis is an overview of the amount of accidents which Uber has had over 1 year.

Quite clearly, the data is showing for England, UK. However, it is very easy to see just how many accidents there are in the differen parts of the country. From this, it's easy to conclude that there is an esceptionally high number of crashes in London. 

This visual can be replicated for any country. It can show us, for example, the density of pickups or deliveries in certain geographic regions. It can also help us, for example, complete some Centre-of-Gravity analysis to determine the ideal locations to establish a new warehouse. Or the routes which our Drivers should go to have the most efficient delivery route.

Again, the beauty of this visual is in it's simplicity and it's usability.

Just imagine what we can do with our own internal data.
""")

# Define a layer to display on a map
layer = pdk.Layer \
    ( 'HexagonLayer'
    , "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv"
    , get_position=['lng', 'lat']
    , auto_highlight=True
    , elevation_scale=50
    , pickable=True
    , elevation_range=[0, 3000]
    , extruded=True
    , coverage=1
    )

# Set the viewport location
# A deck.gl Viewport is essentially a geospatially enabled camera, 
# and combines a number of responsibilities, which can project and 
# unproject 3D coordinates to the screen.
view_state = pdk.ViewState \
    ( longitude=-1.415
    , latitude=52.2323
    , zoom=6
    , min_zoom=5
    , max_zoom=15
    , pitch=40.5
    , bearing=-27.36
    )

# Render the map in Streamlit map
deckchart = st.pydeck_chart \
    ( pdk.Deck \
        ( initial_view_state=view_state
        , layers=[layer]
        )
    )

# Protips
st.markdown(unsafe_allow_html=True, body=
"""
**ProTips:**

1. <img src="https://icons-for-free.com/iconfiles/png/512/move-1321215623357277485.png" width=30></img> To pan : `click` & drag
2. <img src="https://icons-for-free.com/iconfiles/png/512/zoom+icon-1320166878528919604.png" width=30></img>To zoom: `scroll` up & down
3. <img src="https://icons-for-free.com/iconfiles/png/512/rotate+icon-1320166903129623074.png" width=30></img> To rotate: `ctrl`+`click` & drag
"""
)

# Subheader
st.subheader("To see the raw data, check:")

# Add Cars data
if st.checkbox("See Accidents Data"):
    download_csv(carsDF)
    st.write('Uber Accidents data')
    st.write(carsDF.head())
