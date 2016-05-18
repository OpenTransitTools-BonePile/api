from datetime import datetime

from flask import jsonify, Flask
from webargs import fields, validate
from webargs.flaskparser import use_args

app = Flask(__name__)
base_url = 'https://developer.trimet.org/ws/v2/trips'

now = datetime.now()
planner_args = {
    'app_id': fields.Str(
        required=True),
    'arrive_by': fields.Bool(
        missing=False),
    # 'bike_custom': fields.List(fields.Float()),
    'bike_type': fields.Str(
        missing='bike_friendly',
        validate=validate.OneOf(['bike_friendly', 'custom', 'quick'])),
    'bike_max': fields.Float(
        missing=3,
        validate=validate.Range(min=0.1)),
    'date': fields.Date(
        missing=now.strftime('%Y-%m-%d')),
    'format': fields.Str(
        missing='JSON',
        validate=validate.OneOf(['JSON', 'XML'])),
    'from': fields.Str(
        required=True),
    'itineraries_max': fields.Int(
        missing=3,
        validate=validate.Range(min=1, max=6)),
    'mode': fields.Str(
        missing='transit',
        validate=validate.OneOf(['bicycle', 'bus', 'train', 'transit',
                                 'transit+bicycle' 'walk'])),
    'time': fields.Time(
        missing=now.strftime('%H:%M:%S')),
    'to': fields.Str(
        required=True),
    'transit_type': fields.Str(
        missing='quick',
        validate=validate.OneOf(['min_transfers', 'quick'])),
    'walk_max': fields.Float(
        missing=0.5,
        validate=validate.Range(min=0.1))
}


@app.route('/tripplanner', methods=['GET'])
@use_args(planner_args)
def plan_trip(args):
    # app.logger.debug(request.args)
    app.logger.debug(args)

    ret_val = jsonify(error=False)
    return ret_val


@app.errorhandler(422)
def handle_validation_error(err):
    exc = err.data['exc']
    return jsonify({'errors': exc.messages}), 422


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
