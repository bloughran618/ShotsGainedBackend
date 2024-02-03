import json

shots_table = [
    # Distance, Tee, Fairway, Rough, Sand, Recovery
    [10,   None,  2.20, 2.49, 2.41, None],
    [15,   None,  2.30, 2.54, 2.47, None],
    [20,   None,  2.40, 2.59, 2.53, None],
    [25,   None,  2.45, 2.64, 2.59, None],
    [30,   None,  2.50, 2.69, 2.67, None],
    [35,   None,  2.55, 2.74, 2.76, None],
    [40,   None,  2.60, 2.78, 2.82, None],
    [45,   None,  2.62, 2.82, 2.90, None],
    [50,   None,  2.65, 2.85, 2.98, None],
    [55,   None,  2.67, 2.88, 3.07, None],
    [60,   None,  2.70, 2.91, 3.15, None],
    [65,   None,  2.72, 2.92, 3.17, None],
    [70,   None,  2.73, 2.93, 3.19, None],
    [75,   None,  2.74, 2.95, 3.22, None],
    [80,   None,  2.75, 2.96, 3.24, None],
    [85,   None,  2.77, 2.97, 3.24, None],
    [90,   None,  2.78, 2.99, 3.23, None],
    [95,   None,  2.79, 3.01, 3.23, None],
    [100,  2.92,  2.80, 3.02, 3.23, 3.80],
    [105,  2.93,  2.81, 3.03, 3.23, 3.80],
    [110,  2.95,  2.83, 3.04, 3.22, 3.80],
    [115,  2.97,  2.84, 3.06, 3.21, 3.80],
    [120,  2.99,  2.85, 3.08, 3.21, 3.78],
    [125,  2.99,  2.86, 3.09, 3.21, 3.78],
    [130,  2.97,  2.88, 3.11, 3.21, 3.78],
    [135,  2.97,  2.90, 3.13, 3.22, 3.78],
    [140,  2.97,  2.91, 3.15, 3.22, 3.80],
    [145,  2.97,  2.93, 3.17, 3.23, 3.80],
    [150,  2.99,  2.95, 3.19, 3.25, 3.80],
    [155,  2.99,  2.97, 3.21, 3.26, 3.80],
    [160,  2.99,  2.98, 3.23, 3.28, 3.81],
    [165,  3.01,  3.00, 3.25, 3.30, 3.81],
    [170,  3.02,  3.03, 3.27, 3.33, 3.81],
    [175,  3.04,  3.06, 3.29, 3.36, 3.81],
    [180,  3.05,  3.08, 3.31, 3.40, 3.82],
    [185,  3.07,  3.11, 3.34, 3.43, 3.83],
    [190,  3.09,  3.13, 3.37, 3.47, 3.84],
    [195,  3.11,  3.16, 3.40, 3.51, 3.86],
    [200,  3.12,  3.19, 3.42, 3.55, 3.87],
    [210,  3.14,  3.26, 3.48, 3.62, 3.89],
    [220,  3.17,  3.32, 3.53, 3.70, 3.92],
    [230,  3.21,  3.39, 3.80, 3.77, 3.95],
    [240,  3.25,  3.45, 3.64, 3.84, 3.97],
    [250,  3.35,  3.52, 3.69, 3.88, 4.00],
    [260,  3.45,  3.58, 3.74, 3.93, 4.03],
    [270,  3.55,  3.63, 3.78, 3.96, 4.07],
    [280,  3.65,  3.69, 3.83, 4.00, 4.10],
    [290,  3.68,  3.74, 3.87, 4.02, 4.15],
    [300,  3.71,  3.78, 3.90, 4.04, 4.20],
    [320,  3.79,  3.84, 3.95, 4.12, 4.31],
    [340,  3.86,  3.88, 4.02, 4.26, 4.44],
    [360,  3.92,  3.95, 4.11, 4.41, 4.56],
    [380,  3.96,  4.03, 4.21, 4.55, 4.66],
    [400,  3.99,  4.11, 4.30, 4.69, 4.75],
    [420,  4.02,  4.15, 4.34, 4.73, 4.79],
    [440,  4.08,  4.20, 4.39, 4.78, 4.84],
    [460,  4.17,  4.29, 4.48, 4.87, 4.93],
    [480,  4.28,  4.40, 4.59, 4.98, 5.04],
    [500,  4.41,  4.53, 4.72, 5.11, 5.17],
    [520,  4.54,  4.85, 4.85, 5.24, 5.30],
    [540,  4.65,  4.97, 4.97, 5.36, 5.42],
    [560,  4.74,  5.05, 5.05, 5.44, 5.50],
    [580,  4.79,  5.10, 5.10, 5.49, 5.55],
    [600,  4.82,  5.13, 5.13, 5.52, 5.58]
]

putts_table = [
    # Distance, Green
    [1,  1.00],
    [3,  1.04],
    [4,  1.13],
    [5,  1.23],
    [6,  1.34],
    [7,  1.42],
    [8,  1.50],
    [9,  1.56],
    [10, 1.61],
    [15, 1.78],
    [20, 1.87],
    [30, 1.98],
    [40, 2.06],
    [50, 2.14],
    [60, 2.21],
    [90, 2.40],
]


def lookup_shot_gained(distance, type):
    if distance == 0:
        return 0

    type = type.lower()
    type_indexes = {
        "tee": 1,
        "fairway": 2,
        "rough": 3,
        "sand": 4,
        "recovery": 5
    }

    # get the index for the shot type
    if type != "green":
        try:
            type_index = type_indexes[type]
        except KeyError:
            raise RuntimeError(f"Invalid Type: {type} is not in {type_indexes.keys()}")

    # get the index for the distance
    distance_index = 0
    try:
        if type == "green":
            while putts_table[distance_index][0] < distance:
                distance_index += 1
        else:
            while shots_table[distance_index][0] < distance:
                distance_index += 1
    except IndexError:
        distance_index = len(shots_table)-1

    if type == "green":
        return putts_table[distance_index][1]

    return shots_table[distance_index][type_index]


def get_shot_gained(from_distance, from_type, to_distance, to_type, shots=1):
    start_shots_gained = lookup_shot_gained(from_distance, from_type)
    end_shots_gained = lookup_shot_gained(to_distance, to_type)
    return round(start_shots_gained - end_shots_gained - shots, 2)


def lambda_handler(event, context):
    # expecting event like
    # {
    #   from: {distance: 450, type: TEE},
    #   to: {distance: 115, type: FAIRWAY}
    # }
    try:
        body = json.loads(event.get('body'))
        from_distance = body['from']['distance']
        from_type = body['from']['type']
        to_distance = body['to']['distance']
        to_type = body['to']['type']
    except KeyError:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': 'Malformed event body, does not look like # {from: {distance: 450, type: TEE}, to: {distance: 115, type: FAIRWAY}}',
                'input': body
            }),
        }

    shots_gained = get_shot_gained(from_distance, from_type, to_distance, to_type)

    return {
        'statusCode': 200,
        'body': json.dumps({
            'shots_gained': shots_gained
        }),
    }


# eventual tests
# print(lookup_shot_gained(450, "Tee"))
# # print(lookup_shot_gained(450, "House"))
# print(lookup_shot_gained(115, "Fairway"))
# print(lookup_shot_gained(10, "Green"))
# print(lookup_shot_gained(900, "ROUGH"))
#
# print(get_shot_gained(450, "Tee", 115, "Fairway"))
# print(get_shot_gained(115, "fairway", 10, "GREEN"))
# print(get_shot_gained(10, "Green", 0, "asdf"))
