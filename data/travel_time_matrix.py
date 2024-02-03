# -*- coding: utf-8 -*-
"""travel-time-matrix.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_HUcpmUwX_I1cpR43jO7j5LKvRhei6GJ
"""

import numpy as np
import requests
import json
import datetime

# (lat, lon, name)
coordinates = [
    (48.1374, 11.5754, "Marien platz"),
    (48.1755, 11.5518, "Olympia"),
    (48.1340, 11.5676, "Sendlinger Tor"),
    (48.1114, 11.4703, "Klinikum Großhadern"),
    (48.2648, 11.6713, "Garching-Forschungszentrum"),
    (48.2489, 11.6532, "Garching"),
    (48.2474, 11.6310, "Garching-Hochbrück"),
    (48.2123, 11.6279, "Fröttmaning"),
    (48.2038, 11.6133, "Kieferngarten"),
    (48.2012, 11.6146, "Freimann"),
    (48.1832, 11.6077, "Studentenstadt"),
    (48.1792, 11.5999, "Alte Heide"),
    (48.1753, 11.6031, "Nordfriedhof"),
    (48.1672, 11.5909, "Dietlindenstraße"),
    (48.1632, 11.5869, "Münchner Freiheit"),
    (48.1565, 11.5840, "Giselastraße"),
    (48.3321, 10.8957, "Universität"),
    (48.1436, 11.5779, "Odeonsplatz"),
    (48.1257, 11.5506, "Poccistraße"),
    (48.1170, 11.5358, "Harras"),
    (48.1152, 11.5198, "Westpark"),
    (48.1160, 11.5022, "Holzapfelkreuth"),
    (48.1231, 11.4840, "Haderner"),
    (48.1811, 11.5115, "Moosach"),
    (48.1833, 11.5316, "Olympia-Einkaufszentrum"),
    (48.1861, 11.5468, "Oberwiesenfeld"),
    (48.1713, 11.5729, "Scheidplatz"),
    (48.1667, 11.5782, "Bonner Platz"),
    (48.1296, 11.5584, "Goetheplatz"),
    (48.0768, 11.5120, "Thalkirchen"),
    (48.0884, 11.4810, "Fürstenried West"),
    (48.1330, 11.5317, "Heimeranplatz"),
    (48.1363, 11.5532, "Theresienwiese"),
    (48.1403, 11.5600, "Hauptbahnhof"),
    (48.1392, 11.5662, "Karlsplatz"),
    (48.1356, 11.5989, "Max-Weber-Platz"),
    (48.1533, 11.6203, "Arabellapark"),
    (48.1354, 11.5019, "Laimer Platz"),
    (48.1360, 11.5382, "Schwanthalerhöhe"),
    (48.1274, 11.6050, "Ostbahnhof"),
    (48.1207, 11.6200, "Innsbrucker Ring"),
    (48.1012, 11.6462, "Neuperlach Zentrum"),
    (48.0890, 11.6451, "Neuperlach Süd"),
    (48.1334, 11.6906, "Messestadt"),
    (48.1287, 11.6835, "Trudering"),
    (48.1124, 11.5878, "Untersbergstraße"),
    (48.1129, 11.5928, "Giesing"),
    (48.1155, 11.5797, "Silberhornstraße"),
    (48.1266, 11.6338, "Josephsburg"),
    (48.1198, 11.5768, "Kolumbusplatz"),
    (48.1457, 11.5653, "Königsplatz"),
    (48.1621, 11.5687, "Hohenzollernplatz"),
    (48.2106, 11.5722, "Milbertshofen"),
    (48.2115, 11.5132, "Hasenbergl"),
    (48.1701, 11.5244, "Westfriedhof"),
    (48.1479, 11.5570, "Stiglmaierplatz"),
    (48.1130, 11.5716, "Candidplatz"),
    (48.0972, 11.5793, "Mangfallplatz"),
]

# Take the first 25 coordinates
coordinates = coordinates[0:25]

ACCESS_TOKEN = ""


class Mapbox:
    access_token: str

    def __init__(self, access_token: str):
        self.access_token = access_token

    def get_endpoint(self, coordinates, profile, depart_at):
        """Constructs an HTTP endpoint URL to which you can send a GET request."""
        param_coordinates = ";".join([f"{lon},{lat}" for lat, lon, name in coordinates])
        param_depart_at = f"depart_at={depart_at}" if depart_at else ""
        endpoint = f"https://api.mapbox.com/directions-matrix/v1/mapbox/{profile}/{param_coordinates}?{param_depart_at}&access_token={self.access_token}"
        return endpoint

    def get_duration_matrix(self, coordinates, profile="driving", depart_at=None):
        """Returns the duration matrix for the given coordinate list and profile."""
        endpoint = self.get_endpoint(coordinates, profile, depart_at)
        response = requests.get(endpoint)
        return json.loads(response.text)


"""Traffic coefficient at index i is multipled with the duration matrix at time slice i"""
traffic_coefficients = {
    0: 1.3,  # 08:00
    1: 1.3,  # 09:00
    2: 1.3,  # 10:00
    3: 1.3,  # 11:00
    4: 1.0,  # 12:00
    5: 1.0,  # 13:00
    6: 1.0,  # 14:00
    7: 1.3,  # 15:00
    8: 1.3,  # 16:00
    9: 1.3,  # 17:00
    10: 0.7,  # 18:00
    11: 0.7,  # 19:00
}


def main(ACCESS_TOKEN=""):

    # Initialize mapbox client
    mapbox = Mapbox(ACCESS_TOKEN)

    # Request duration matrix from mapbox
    mapbox_response = mapbox.get_duration_matrix(coordinates)

    # Update the durations if request was successful
    if "durations" not in mapbox_response:
        print("Mapbox access key not provided!")
        return
    durations = mapbox_response["durations"]

    # Construct 12 slices of 2D duration matrices
    tdd_matrix = [np.array(durations) * traffic_coefficients[time] for time in range(0, 12)]

    # Transpose the matrix into i,j,t form
    tdd_matrix = np.transpose(np.array(tdd_matrix), (1, 2, 0))

    # get the datetime and set the name accordingly
    # current_date = datetime.datetime.now()

    output_file_name = "matrix"  # + str(current_date)

    # Save the time-dependent duration matrix as .npy
    np.save(output_file_name, tdd_matrix)

    # save the name of the last retrieved duration time matrix
    # with open('matrix_name.txt', 'w') as f:
    #    f.write(output_file_name)

    return tdd_matrix


# matrix = main()
# print(matrix)
