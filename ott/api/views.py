from datetime import datetime

# from apispec import APISpec
# from apispec.ext.marshmallow.swagger import fields2parameters
from flask import jsonify, Flask
from flask_restful import Api, Resource
from webargs import fields, validate
from webargs.flaskparser import parser, use_kwargs

from ott.api.models import ResponseSchema
# from ott.otp_client.trip_planner import TripPlanner

# otp api code, master branch:
# https://github.com/opentripplanner/OpenTripPlanner/blob/master/src/main/java/org/opentripplanner/api/common/RoutingResource.java
# otp api code, TriMet release (~0.10)
# https://github.com/opentripplanner/OpenTripPlanner/blob/3eda2fa511f8404422dcff02a8d018f65833cbdd/otp-rest-api/src/main/java/org/opentripplanner/api/common/RoutingResource.java
# otp api codes for 0.15.0
# http://dev.opentripplanner.org/apidoc/0.15.0/resource_PlannerResource.html

app = Flask(__name__)
api = Api(app)
# spec = APISpec(
#     title='Trip Planner',
#     version='2.0.0',
#     info=dict(
#         description='A trip planning API powered by OpenTripPlanner'),
#     plugins=(
#         'apispec.ext.marshmallow',
#         'apispec.ext.flask')
# )

base_url = 'https://developer.trimet.org/ws/v2.0/trips'
now = datetime.now()

planner_args = {
    'appID': fields.Str(
        required=True),
    'arriveBy': fields.Bool(
        missing=False),
    'bikeOptimize': fields.Str(
        missing='bike_friendly',
        validate=validate.OneOf(['bike_friendly', 'flat',
                                 'greenways', 'quick'])),
    'bikeMaxDistance': fields.Float(
        missing=3,
        validate=validate.Range(min=0.1)),
    'bikeSafetyFactor': fields.Float(
        missing=1/3,
        validate=validate.Range(min=0, max=1)),
    'bikeSlopeFactor': fields.Float(
        missing=1/3,
        validate=validate.Range(min=0, max=1)),
    'bikeSpeed': fields.Float(
        validate=validate.Range(min=1, max=30)),
    'bikeTimeFactor': fields.Float(
        missing=1/3,
        validate=validate.Range(min=0, max=1)),
    'date': fields.Date(
        default='date of the api call',
        missing=now.strftime('%Y-%m-%d')),
    'from': fields.Str(
        required=True),
    'itinerariesMax': fields.Int(
        missing=3,
        validate=validate.Range(min=1, max=6)),
    'mode': fields.Str(
        missing='transit',
        validate=validate.OneOf(['bicycle', 'bus', 'train', 'transit',
                                 'transit,bicycle' 'walk'])),
    'responseFormat': fields.Str(
        missing='JSON',
        validate=validate.OneOf(['JSON', 'XML'])),
    'time': fields.Time(
        default='time of the api call',
        missing=now.strftime('%H:%M:%S')),
    'to': fields.Str(
        required=True),
    'transitOptimize': fields.Str(
        missing='quick',
        validate=validate.OneOf(['quick', 'transfers'])),
    'transferPenalty': fields.Int(
        ),
    'walkMaxDistance': fields.Float(
        missing=0.5,
        validate=validate.Range(min=0.1)),
    'walkSpeed': fields.Float(
        description='ignored for trips involving bikes',
        validate=validate.Range(min=0.1, max=15)
    )
}

# use this function to convert the parameters to openapi doc format
# from pprint import pprint
# pprint(fields2parameters(planner_args)[0], width=120)
# exit()

# the following parameters are a part otp's api, but aren't being exposed to
# the public because they're either a headache to deal with (and we've figured
# out rational defaults) or they are part of features that we don't support:
# unsupported -
# intermediatePlaces, wheelchair, preferredAgencies, unpreferredAgencies,
# showIntermediateStops, preferredRoutes, otherThanPreferredRoutesPenalty,
# unpreferredRoutes, bannedAgencies, bannedTrips, bannedStops (!0.10),
# bannedStopsHard (!0.10)
# (don't know if this is supported by ott)
# config headaches -
# maxPreTransitTime, walkReluctance, waitReluctance, waitAtBeginningFactor
# (not in 0.10.0), bikeSwitchTime (!0.10), bikeSwitchCost (!0.10),
# minTransferTime,  walkBoardCost (!0.10), bikeBoardCost (!0.10)


# using webargs with flask-restful:
# https://github.com/sloria/webargs/issues/19
# https://github.com/sloria/webargs/blob/dev/examples/flaskrestful_example.py


class TripPlan(Resource):
    @use_kwargs(planner_args)
    def get(self):
        """returns a trip plann if valid parameters are supplied
        ---
        get:
            description: Get a trip plan
            responses:
            -200:
                description: A trip plan to be returned
                schema: ResponseSchema
        """

        return {'what is this?': 'a test!!'}
        # print responseFormat

        # planner = TripPlanner(otp_url="http://maps.trimet.org/prod",
        #                       solr='http://maps.trimet.org/solr')

api.add_resource(TripPlan, '/trip_planner')


# @app.route('/tripplanner', methods=['GET'])
# @use_args(planner_args)
# def plan_trip(args):
#     # app.logger.debug(request.args)
#     app.logger.debug(args)
#
#     ret_val = jsonify(error=False)
#     return ret_val
#
#
# @app.errorhandler(422)
# def handle_validation_error(err):
#     exc = err.data['exc']
#     return jsonify({'errors': exc.messages}), 422


if __name__ == '__main__':
    app.run(debug=True)
