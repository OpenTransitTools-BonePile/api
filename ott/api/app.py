from flask import jsonify, request, Flask
from webargs import fields
from webargs.flaskparser import parser

app = Flask(__name__)
base_url = 'https://developer.trimet.org/ws/v2/trips'
planner_args = {
    'from': fields.Str(required=True),
    'mode': fields.Str(required=True),
    'to': fields.Str(required=True)
}


@app.route('/tripplanner', methods=['GET'])
def plan_trip():
    # app.logger.debug(request.args)
    args = parser.parse(planner_args, request)
    app.logger.debug(args)

    ret_val = jsonify(error=False)
    return ret_val


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
