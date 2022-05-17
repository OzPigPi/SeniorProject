from flask import Flask,jsonify, request
from flask_restful import Resource, Api
#from flask_restful import Api, Resource
import pandas as pd, requests, json



app = Flask(__name__)
api = Api(app)
# method to calculate top facilities by sending get request from framework(FLUTTER)
class FlutterRequest(Resource):
    def get(self, token):
        # Load Facilities Meta_data

        mr = requests.get("https://senior-project-booking-default-rtdb.firebaseio.com/facilities.json?auth="+token).content.decode()
        metadata = pd.read_json(mr)

        #metadata = pd.read_json("https://senior-project-booking-default-rtdb.firebaseio.com/facilities.json?auth=" + token)

        print(metadata)
        C = metadata['vote_avg'].mean()

        # Calculate the minimum number of votes required to be in the chart, m
        m = metadata['vote_coun'].min()
        # Filter out all facilities
        resources = metadata.copy().loc[metadata['vote_coun'] >= m]

        def weighted_rating(x, m=m, C=C):
            v = x['vote_coun']
            R = x['vote_avg']

            if (v + m != 0):
                return (v / (v + m) * R) + (m / (m + v) * C)
            else:
                return 0

        resources['score'] = resources.apply(weighted_rating, axis=1)

        # Sort the facilities based on score calculated above
        resources = resources.sort_values('score', ascending=False)



        return resources['id'].to_json(orient='split', index=False)


api.add_resource(FlutterRequest, "/<string:token>")
if __name__ == '__main__':
     app.run(debug=False,host='0.0.0.0')