import streamlit as st
import folium
import requests
import pandas as pd
from geopy.distance import geodesic
import streamlit.components.v1 as components

def is_outside_geofences(current_location, geofences):
    for geofence_center, radius in geofences:
        distance = geodesic(current_location, geofence_center).meters
        if distance <= radius:
            return False
    return True

def get_user_location():
    try:
        # Create a custom HTML component to get the user's geolocation
        location_script = """
            <script>
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        function(position) {
                            const latitude = position.coords.latitude;
                            const longitude = position.coords.longitude;
                            const locationString = `${latitude},${longitude}`;
                            window.parent.document.getElementById("user-location").value = locationString;
                        },
                        function(error) {
                            console.error("Error getting location:", error);
                        }
                    );
                } else {
                    console.error("Geolocation is not supported by this browser.");
                }
            </script>
            <input type="text" id="user-location" />
        """
        components.html(location_script, height=100)

        # Get the user's location from the input field
        user_location_string = st.session_state.get("user_location", None)
        if user_location_string:
            return user_location_string.split(",")
        else:
            return None
    except Exception as e:
        st.warning(f"Error getting user location: {e}")
        return None

def read_geofences_from_csv(csv_path):
    df = pd.read_csv(csv_path)
    geofences = [((row['Latitude'], row['Longitude']), row['Radius']) for _, row in df.iterrows()]
    return geofences

def main():
    st.title("Road Accident App")

    # Specify the path to your CSV file containing geofence data
    csv_path = "gv.csv"

    # Read geofence data from CSV and create the geofences list
    geofences = read_geofences_from_csv(csv_path)

    # Get user location based on Geolocation API
    user_location = get_user_location()
    if user_location:
        user_location = [float(coord) for coord in user_location]
    else:
        st.warning("Could not get user location. Please allow location access or enter your location manually.")

    if user_location:
        st.write(f"User Location: Latitude: {user_location[0]}, Longitude: {user_location[1]}")

        # Check if the user's location is outside any of the geofences
        outside_geofences = is_outside_geofences(user_location, geofences)

        # Display result
        if outside_geofences:
            st.success("Safe to navigate")
        else:
            st.error("Beware! You are in an Accident Prone Region")

        # Display the Folium map with geofences and user's location
        m = folium.Map(location=user_location, zoom_start=5)

        # Plot each geofence on the map
        for geofence_center, radius in geofences:
            folium.Circle(geofence_center, radius=radius, color='red', fill=True, fill_color='red').add_to(m)

        folium.Marker(user_location, popup="User Location", icon=folium.Icon(color='blue')).add_to(m)

        # Convert Folium map to HTML and display using st.markdown
        map_html = m._repr_html_()
        st.markdown(map_html, unsafe_allow_html=True)

if __name__ == "__main__":
    if "user_location" not in st.session_state:
        st.session_state["user_location"] = None

    main()