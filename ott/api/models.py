from marshmallow import fields, Schema


class AlertSchema(Schema):
    future = fields.Bool()
    long_term = fields.Bool()
    route_id = fields.Str()
    start_date = fields.Int()
    start_date_pretty = fields.Str()
    start_time_pretty = fields.Str()
    text = fields.Str()
    type = fields.Str()
    url = fields.Url()


class DistanceSchema(Schema):
    distance = fields.Int()
    measure = fields.Str()


class DateInfoSchema(Schema):
    bike_time_hours = fields.Int()
    bike_time_mins = fields.Int()
    date = fields.Str()
    day = fields.Int()
    duration = fields.Str()
    duration_min = fields.Int()
    duration_ms = fields.Int()
    end_time = fields.Str()
    extended = fields.Bool()
    month = fields.Int()
    pretty_date = fields.Str()
    start_time = fields.Str()
    start_time_ms = fields.Int()
    total_time_hours = fields.Int()
    total_time_mins = fields.Int()
    transit_time_hours = fields.Int()
    transit_time_mins = fields.Int()
    wait_time_hours = fields.Int()
    wait_time_mins = fields.Int()
    walk_time_hours = fields.Int()
    walk_time_mins = fields.Int()
    year = fields.Int()


class GradeSchema(Schema):
    dd = fields.Float()
    de = fields.Float()
    down = fields.Float()
    ud = fields.Float()
    ue = fields.Float()
    up = fields.Float()


class ElevationSchema(Schema):
    distance = fields.Float()
    end_ft = fields.Float()
    fall_ft = fields.Float()
    grade = fields.Nested(GradeSchema)
    high_ft = fields.Float()
    low_ft = fields.Float()
    points = fields.Str()
    points_array = fields.List(fields.Float)
    rise_ft = fields.Float()
    start_ft = fields.Float()


class ErrorSchema(Schema):
    id = fields.Int()
    msg = fields.Str()


class FareSchema(Schema):
    adult = fields.Str()


class LocationSchema(Schema):
    """for 'to' and 'from' objects"""

    lat = fields.Float()
    lon = fields.Float()
    map_img = fields.Url
    name = fields.Str()
    stop = fields.Str()


class StepSchema(Schema):
    compass_direction = fields.Str()
    distance = fields.Nested(DistanceSchema)
    distance_feet = fields.Float()
    distance_meters = fields.Float()
    lat = fields.Float()
    lon = fields.Float()
    name = fields.Str()
    relative_direction = fields.Str()


class LegSchema(Schema):
    alerts = fields.Nested(AlertSchema)
    compass_direction = fields.Str()
    date_info = fields.Nested(DateInfoSchema)
    distance = fields.Nested(DistanceSchema)
    distance_feet = fields.Float()
    distance_meters = fields.Float()
    elevation = fields.Nested(ElevationSchema)
    from_ = fields.Nested(LocationSchema)
    interline = fields.Bool()
    mode = fields.Str()
    route = fields.Str()
    steps = fields.List(fields.Nested(StepSchema))
    to = fields.Nested(LocationSchema)
    transfer = fields.Bool()


class ItinerarySchema(Schema):
    alerts = fields.List(fields.Nested(AlertSchema))
    date_info = fields.Nested(DateInfoSchema)
    dominant_mode = fields.Str()
    fare = fields.Nested(FareSchema)
    has_alerts = fields.Bool()
    itin_num = fields.Int()
    legs = fields.List(fields.Nested(LegSchema))
    selected = fields.Bool()
    transfers = fields.Int()
    url = fields.Url


class PlanSchema(Schema):
    from_ = fields.Nested(LocationSchema, load_from='from', dump_to='from')
    itineraries = fields.List(fields.Nested(ItinerarySchema))
    to = fields.Nested(LocationSchema)


# start here: all other schemas are nested or sub-nested with the
# ResponseSchema
class ResponseSchema(Schema):
    error = fields.Nested(ErrorSchema)
    plan = fields.Nested(PlanSchema)
