from flask import Flask, render_template, jsonify, send_from_directory
import requests

app = Flask(__name__)

class Bus:
    def __init__(self, route_no, interval, density, image_bunch, location):
        self.route_no = route_no
        self.interval = interval
        self.density = density
        self.image_bunch = image_bunch
        self.location = location

    def update(self):
        def get_crowd_data_from_overpass(location):
            bbox = f"{location[0]},{location[1]},{location[2]},{location[3]}"
            url = f"https://overpass-api.de/api/interpreter?data=[out:json];node['amenity'='bus_stop']({bbox});out;"
            try:
                response = requests.get(url)
                data = response.json()
                return len(data['elements'])
            except Exception as e:
                print(f"Error fetching data from Overpass API: {e}")
                return 0

        try:
            crowd_data = get_crowd_data_from_overpass(self.location)
            if crowd_data > 50:
                self.density = 85
            elif crowd_data > 20:
                self.density = 60
            else:
                self.density = 20

            if self.density > 80:
                self.interval = max(5, self.interval - 2)
            elif self.density < 30:
                self.interval = min(30, self.interval + 5)
        except Exception as e:
            print(f"Error processing Route {self.route_no}: {e}")

@app.route('/update_routes_twice')
def update_routes_twice():
    route_1_location = [37.7749, -122.4194, 37.8049, -122.3894]
    route_2_location = [40.7128, -74.0060, 40.7428, -73.9760]
    route_3_location = [51.5074, -0.1278, 51.5374, -0.0978]

    route_1_images = ["/home/sathwiksg07/python-venv/image1.png", "/home/sathwiksg07/python-venv/image2.png"]
    route_2_images = ["/home/sathwiksg07/python-venv/image3.jpg", "/home/sathwiksg07/python-venv/image4.jpg"]
    route_3_images = ["/home/sathwiksg07/python-venv/image5.jpg", "/home/sathwiksg07/python-venv/image6.jpg"]

    route_1 = Bus(route_no=1, interval=15, density=40, image_bunch=route_1_images, location=route_1_location)
    route_2 = Bus(route_no=2, interval=5, density=85, image_bunch=route_2_images, location=route_2_location)
    route_3 = Bus(route_no=3, interval=20, density=10, image_bunch=route_3_images, location=route_3_location)

    routes = [route_1, route_2, route_3]
    updates = []
    for _ in range(2):
        for route in routes:
            route.update()
        updates.append([
            {
                'route': route.route_no,
                'interval': route.interval,
                'density': route.density,
                'status': 'High density' if route.density > 80 else 'Moderate density' if route.density > 30 else 'Low density'
            }
            for route in routes
        ])
    
    return jsonify(updates)

@app.route('/ws/ws')
def handle_invalid_request():
    return 'Invalid request', 400

@app.route('/')
def index():
    return render_template('bus_frontend.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'bus.svg', mimetype='image/svg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
