import osmnx as ox
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np
import matplotlib.animation as animation
from geopandas import GeoDataFrame
from shapely.geometry import Point

# Function to parse coordinates
def parse_coordinates(coord_str):
    if isinstance(coord_str, str):
        matches = re.match(r'(\d+\.\d+)°N (\d+\.\d+)°E', coord_str)
        if matches:
            lat = float(matches.group(1))
            lon = float(matches.group(2))
        else:
            lat = None
            lon = None
    else:
        lat = None
        lon = None
    return lat, lon

# Load the lighthouse data
lighthouses = pd.read_csv('light - Sheet1.csv')

# Parse the coordinates
lighthouses['Latitude'], lighthouses['Longitude'] = zip(*lighthouses['Coordinates'].map(parse_coordinates))

# Calculate the age of the lighthouses
current_year = 2023  # Update this as needed
lighthouses['Age'] = current_year - lighthouses['first lit']

# Normalize the age values between 0 and 1 for color mapping
lighthouses['Age_norm'] = (lighthouses['Age'] - lighthouses['Age'].min()) / (lighthouses['Age'].max() - lighthouses['Age'].min())

# Convert the lighthouses DataFrame to a GeoDataFrame
geometry = [Point(xy) for xy in zip(lighthouses['Longitude'], lighthouses['Latitude'])]
lighthouses_geo = GeoDataFrame(lighthouses, geometry=geometry)

# Set the initial CRS of the lighthouses GeoDataFrame to match the original Norway CRS
lighthouses_geo.crs = "EPSG:4326"

# Load the high-resolution world map
world = gpd.read_file('ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')

# Extract Norway map (excluding Svalbard)
norway = world[(world['NAME'] == 'Norway') &
               (world['geometry'].apply(lambda geo: geo.centroid.y < 70))]

# Change the CRS to the Mercator projection
norway = norway.to_crs("EPSG:3395")  # Mercator projection
lighthouses_geo = lighthouses_geo.to_crs("EPSG:3395")  # Same projection for the lighthouses

# Create the plot
fig, ax = plt.subplots(figsize=(40, 40))

# Function to update the plot for each frame
def update(num):
    ax.clear()
    norway.plot(ax=ax, color='lightgray', edgecolor='white')
    ax.scatter(lighthouses_geo.geometry.x[:num], lighthouses_geo.geometry.y[:num], c=lighthouses_geo['Age_norm'][:num], cmap='YlOrBr', alpha=1)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.title('Lighthouses in Norway')

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=len(lighthouses_geo), repeat=True)

# Save the animation as a GIF
ani.save('lighthouses_in_norway.gif', writer='pillow', fps=30)

# Display the plot
#plt.show()
