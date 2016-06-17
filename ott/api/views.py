"""
The following parameters are a part of the otp api, but are not being
exposed in this wrapper to order to provide a simple interface, (!0.10)
means that the parameter did not yet exist in otp v0.10:
- alightSlack
- bannedAgencies
- bannedStops (!0.10)
- bannedStopsHard (!0.10)
- bannedTrips
- batch
- bikeBoardCost (!0.10)
- bikeSwitchCost (!0.10)
- bikeSwitchTime (!0.10)
- boardSlack
- clampInitialWait
- disableRemainingWeightHeuristic (!0.10)
- ignoreRealtimeUpdates (!0.10)
- intermediatePlaces
- locale
- maxPreTransitTime
- maxTransfers
- minTransferTime
- nonpreferredTransferPenalty (!0.10)
- otherThanPreferredRoutesPenalty
- preferredAgencies
- preferredRoutes
- reverseOptimizeOnTheFly
- showIntermediateStops
- startTransitStopId
- startTransitTripId (!0.10)
- triangleSafetyFactor
- triangleSlopeFactor
- triangleTimeFactor
- unpreferredAgencies
- unpreferredRoutes
- waitAtBeginningFactor (!0.10)
- waitReluctance
- walkBoardCost (!0.10)
- walkReluctance
- wheelchair

Pertinent OpenTripPlanner Docs/Code
- otp api code, master branch:
  https://github.com/opentripplanner/OpenTripPlanner/blob/master/src/main/java/org/opentripplanner/api/common/RoutingResource.java
- otp api code, TriMet release (~v0.10)
  https://github.com/opentripplanner/OpenTripPlanner/blob/3eda2fa511f8404422dcff02a8d018f65833cbdd/otp-rest-api/src/main/java/org/opentripplanner/api/common/RoutingResource.java
- otp api docs for 0.20.0
  http://dev.opentripplanner.org/apidoc/0.20.0/resource_PlannerResource.html

Other Resources:
- swagger editor: http://editor.swagger.io/#/
"""

import sys
from inspect import getsourcefile
from os.path import abspath, dirname, join
from pprint import pprint

from apispec import APISpec
from flask import jsonify, Flask
from flask_restful import abort, Api, Resource
from marshmallow import validate
from webargs import fields
from webargs.flaskparser import parser, use_args

from ott.api.models import ResponseSchema
from ott.otp_client.trip_planner import TripPlanner

app = Flask(__name__)
api = Api(app)
spec = APISpec(
    title='Trip Planner',
    version='2.0.0',
    info=dict(
        description='A trip planning API powered by OpenTripPlanner'),
    plugins=(
        'apispec.ext.marshmallow',
        'apispec.ext.flask',
        'ott.api.apispec_ext.flask_restful')
)

BASE_URL = 'https://developer.trimet.org/ws/v2.0/trips'

# parameters names for this api wrapper
APP_ID = 'appID'
ARRIVE_BY = 'arriveBy'
BIKE_OPT = 'bikeOptimize'
BIKE_MAX = 'bikeDistanceMax'
BIKE_SPEED = 'bikeSpeed'
DATE = 'date'
FROM = 'from'
ITIN_MAX = 'itinerariesMax'
MODE = 'mode'
RESP_FORMAT = 'responseFormat'
TIME = 'time'
TO = 'to'
TRANSIT_OPT = 'transitOptimize'
TRANSFER_PEN = 'transferPenalty'
WALK_MAX = 'walkDistanceMax'
WALK_SPEED = 'walkSpeed'

# otp parameters that are not directly exposed, but mapped to by the
# wrapper params
OTP_DIST_MAX = 'maxWalkDistance'
OTP_ITIN_MAX = 'numItineraries'
OTP_OPTIMIZE = 'optimize'

planner_args = {
    APP_ID: fields.Str(
        description='token required to make TriMet web service calls, '
                    'register for a free appID here: '
                    'http://developer.trimet.org/appid/registration/',
        required=True),
    ARRIVE_BY: fields.Bool(
        description='indicates whether or not the time and date of the trip',
        default=False),
    BIKE_OPT: fields.Str(
        default='safe',
        validate=validate.OneOf(['flat', 'greenways', 'quick', 'safe'])),
    BIKE_MAX: fields.Float(
        default='3 miles',
        description='maximum biking distance in miles for the trip, only '
                    'applies to biking+transit trips',
        validate=validate.Range(min=0.1)),
    BIKE_SPEED: fields.Float(
        default='~11 mph',
        description='speed, in miles per hour, from which biking travel time '
                    'estimates will be derived',
        validate=validate.Range(min=1, max=30)),
    DATE: fields.Date(
        default='date of the api call'),
    FROM: fields.Str(
        required=True),
    ITIN_MAX: fields.Int(
        default=3,
        description='maximum number of itineraries (trip options) to return, '
                    'in some cases the trip planner may generate and thus '
                    'return fewer than this number, but it this number will'
                    'not be exceeded',
        validate=validate.Range(min=1, max=6)),
    MODE: fields.Str(
        default='transit',
        validate=validate.OneOf(['bicycle', 'bus', 'train', 'transit',
                                 'transit,bicycle', 'walk'])),
    RESP_FORMAT: fields.Str(
        missing='JSON',
        validate=validate.OneOf(['JSON', 'XML'])),
    TIME: fields.Time(
        default='time of the api call'),
    TO: fields.Str(
        required=True),
    TRANSIT_OPT: fields.Str(
        default='quick',
        validate=validate.OneOf(['quick', 'transfers'])),
    WALK_MAX: fields.Float(
        description='maximum walking distance in miles',
        default=0.5,
        validate=validate.Range(min=0.1)),
    WALK_SPEED: fields.Float(
        default='~3 mph',
        description='speed, in miles per hour, from which walking travel '
                    'time estimates will be derived',
        validate=validate.Range(min=0.1, max=15))
}


class TripPlan(Resource):
    @use_args(planner_args)
    def get(self, args):
        """returns a trip plan if valid parameters are supplied

        ---
        description: Get a trip plan
        responses:
          200:
            description: A trip plan to be returned
            schema: ResponseSchema
        """

        # otp only has one parameter for max walk and max bike distance
        # to avoid confusion they're exposed here as two params and
        # then combined, if they both exist bike overwrites walk, also
        # distance must be converted from miles to meters
        miles_to_meters = 1609.34
        if WALK_MAX in args:
            args[OTP_DIST_MAX] = args.pop(WALK_MAX) * miles_to_meters

        if BIKE_MAX in args:
            args[OTP_DIST_MAX] = args.pop(BIKE_MAX) * miles_to_meters

        # again there is only one optimize parameter that otp takes, but
        # I'm exposing two for clarity, bikeOptimize overwrites transit
        # optimize if they're both supplied
        if TRANSIT_OPT in args:
            args[OTP_OPTIMIZE] = args.pop(TRANSIT_OPT)

            # the 'transfers' optimize option has been deprecated so that
            # functionality is being emulated here by setting a the
            # transferPenalty parameter
            if args[OTP_OPTIMIZE] == 'transfers':
                args[TRANSFER_PEN] = 1800  # seconds
                args[OTP_OPTIMIZE] = 'quick'

        if BIKE_OPT in args:
            args[OTP_OPTIMIZE] = args.pop(BIKE_OPT)

        # I'm using a more descriptive term for the maximum itineraries
        # parameter, but it needs to be converted back to the name that
        # otp accepts
        if ITIN_MAX in args:
            args[OTP_ITIN_MAX] = args.pop(ITIN_MAX)

        # users enter speeds as miles per hours, but otp reads them as
        # as meters per second
        mph_to_mps = 0.44704
        if BIKE_SPEED in args:
            args[BIKE_SPEED] *= mph_to_mps

        if WALK_SPEED in args:
            args[WALK_SPEED] *= mph_to_mps

        response_format = args.pop(RESP_FORMAT)

        otp_url = 'http://maps.trimet.org/prod'
        solr_url = 'http://maps.trimet.org/solr'
        planner = TripPlanner(otp_url=otp_url, solr=solr_url)
        plan = planner.plan_trip(args, pretty=True)
        response_schema = ResponseSchema()
        response, errors = response_schema.dump(plan)

        if response_format == 'XML':
            pass
        elif response_format == 'JSON':
            response = jsonify(response)

        # app.logger.debug(args)

        return response, 200


@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function
    to return a JSON error response to the client.
    """

    not_valid = 'Not a valid choice.'

    # when an invalid choice is made for a parameter, append valid
    # choices to the error message
    for field in err.fields:
        for v in field.validators:
            if isinstance(v, validate.OneOf):
                field_errors = err.messages[field.name]
                if not_valid in field_errors:
                    nv_ix = field_errors.index(not_valid)
                    field_errors[nv_ix] = (
                        '{0}  Select one of the following: {1}'.format(
                            not_valid, v.choices_text))

    abort(err.status_code, errors=err.messages)


if __name__ == '__main__':
    # the value of sys.executable is used to restart the app when
    # debugging, but since buildout kind of uses system python the
    # value of sys.executable must be manually pointed to the
    # executable buildout has created
    home = dirname(dirname(dirname(abspath(getsourcefile(lambda: 0)))))
    sys.executable = join(home, 'bin', 'python')

    api.add_resource(TripPlan, '/trip_planner', )
    spec.definition('Response', schema=ResponseSchema)

    # utilizes apispec extension ott.api.apispec_ext.flask_restful
    spec.add_path(api=api, resource=TripPlan, req_params=planner_args)
    # pprint(spec.to_dict())

    app.run(debug=True)
