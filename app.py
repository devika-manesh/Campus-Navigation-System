from flask import Flask, render_template, request, redirect, url_for, jsonify
import folium
import openrouteservice
from geopy.geocoders import Nominatim
import pandas as pd
import speech_recognition as sr
import pyttsx3

app = Flask(__name__)

# Initialize Text to Speech engine
engine = pyttsx3.init()

# Data
file_path = "project cs.xlsx"
df = pd.read_excel(file_path)

places = {
    'admin': (76.85983445667758, 8.558296623824283),
    'mechanical': (76.86000938250643, 8.558715693710296),
    'canteen': (76.86062860490402, 8.559007450953514),
    'electronics': (76.85977006628079, 8.559102935093623),
    'basketball': (76.86040592144863, 8.557649451701682),
    'civil': (76.86086738668281, 8.55798629962408),
    'auditorium': (76.86054516385475, 8.559458348071377),
    'boys': (76.86136077554683, 8.559384082700474),
    'girls': (76.85913394099283, 8.557771459645002),
    'electrical': (76.85913394099283, 8.557771459645002),
    'cs': (76.860546, 8.558302),
    'cafeteria':(76.861054,8.558296)
}

API_KEY = "5b3ce3597851110001cf6248cc71b5f3b13b488a8a823f8bb89a91af"

# Utility Functions
def check_room(df, string):
    for _, row in df.iterrows():
        name = str(row["name"]).lower()
        direction = row["direction"]
        departm = row["department"]
        if name in string.lower():
            return True, direction, departm
    return False, '', ''

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
        text = recognizer.recognize_google(audio)
        return text

def find_coordinates(input_string, places_dict):
    for place, coordinates in places_dict.items():
        if place in input_string:
            return coordinates
    return None

def create_walking_route_map(api_key, coordinates):
    start_coords = (76.85983445667758, 8.558296623824283)
    end_coords = coordinates
    client = openrouteservice.Client(key=api_key)
    route = client.directions(
        coordinates=[start_coords, end_coords],
        profile='foot-walking',
        format='geojson'
    )
    route_coords = route['features'][0]['geometry']['coordinates']
    route_coords = [(coord[1], coord[0]) for coord in route_coords]
    midpoint = ((start_coords[1] + end_coords[1]) / 2, (start_coords[0] + end_coords[0]) / 2)
    route_map = folium.Map(location=midpoint, zoom_start=30)
    folium.Marker(location=(start_coords[1], start_coords[0]), popup="You are here", icon=folium.Icon(color="green")).add_to(route_map)
    folium.Marker(location=(end_coords[1], end_coords[0]), popup="Destination", icon=folium.Icon(color="red")).add_to(route_map)
    folium.PolyLine(locations=route_coords, color="blue", weight=5).add_to(route_map)
    return route_map

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Validate login (this is just a placeholder)
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':  # Replace with real validation
            return redirect(url_for('input_page'))
        else:
            return "Invalid credentials", 400
    return render_template('login.html')

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    if request.method == 'POST':
        input_string = request.form['input_text']
        print(input_string)
        flag,direction,departm=check_room(df,input_string)

        if flag:
            coordinates = find_coordinates(departm, places)
            # engine.say(direction)
            # engine.runAndWait()
        else:
            coordinates = find_coordinates(input_string.lower(), places)
        
        if coordinates:
            print(f"Coordinates for the place found: {coordinates}")
            try:
                route_map = create_walking_route_map(API_KEY, coordinates)
        
                route_map.save("static/route_map.html")
                print("Walking route map saved as walking_route_map.html")
                return render_template('route_map.html',direction_message=direction)
            except ValueError as e:
                print(e)
        else:
            return "Place not found", 404

    return render_template('input_page.html')

if __name__ == "__main__":
    app.run(debug=True)
