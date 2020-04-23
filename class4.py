import re
import statistics
import json
from numbers import Number


def aggregate_json(dictionary, aggregate_function, slice_scheme=None, non_target_keys=None, target_levels=None):
    """
    Provided the scheme described below, the function will follow it going level by level into the dictionary,
    returning the desired aggregated value (similar to "group by" query in SQL).

    :param dictionary: json-like dictionary.
    :param aggregate_function: function that will take a list of values and return a single value
    :param slice_scheme: string representing where the values to aggregate are.
        It looks like: [key1][key2][key3] and so on. To aggregate the level, replace the key name with ':'.
        If the key of the level is replaced by ':', the function will run recurrently for each key on the level where
        it encountered that symbol, and when it finishes, it will aggregate all the results.
        If slice_scheme is given, the non_target_keys and target_levels will be deducted from it.
    :param non_target_keys: *optional* levels where we want a single key-value from.
    :param target_levels: *optional* levels which we want to aggregate.
        If both non_target_keys and target_levels are provided, the slice_scheme is no longer needed.
    :return: a single value, aggregated from dictionary, based on a slice_scheme.
    """
    non_target_keys = non_target_keys if non_target_keys is not None else []
    target_levels = target_levels if target_levels is not None else []

    if slice_scheme is not None:
        target_levels, non_target_keys = parse_slice_scheme(slice_scheme)

    current_level = dictionary
    level = 0
    while level < len(non_target_keys):
        # searches for first target-level to aggregate
        if level in target_levels:
            break
        else:
            next_non_target_key = non_target_keys[level]
            current_level = current_level[next_non_target_key]
            level += 1

    if isinstance(current_level, list):
        return aggregate_function(current_level)
    elif isinstance(current_level, dict):
        aggregation_of_keys_on_curr_level = [
            aggregate_json(current_level[key], aggregate_function, None, non_target_keys[level:], target_levels[1:])
            for key in current_level.keys()
        ]
        return aggregate_function(aggregation_of_keys_on_curr_level)
    elif isinstance(current_level, Number):
        return current_level
    else:
        raise TypeError('The type you want to aggregate is neither a numerical value nor an array of numerical values.')


def parse_slice_scheme(slice_scheme):
    non_target_keys = []
    target_levels = []
    keys = re.split(pattern=r'\]\[', string=slice_scheme[1:-1])
    for element in range(len(keys)):
        if keys[element] == ':':
            target_levels.append(element)
        else:
            non_target_keys.append(keys[element])
    return target_levels, non_target_keys


if __name__ == '__main__':
    school = {
        "2100": {
            "FirstName": "John",
            "LastName": "Adams",
            "Classes": {
                "English": [1, 2],
                "Maths": [3, 4]
            }
        },
        "2101": {
            "FirstName": "Mat",
            "LastName": "Foo",
            "Classes": {
                "English": [2, 3, 5],
                "Maths": [4, 4]
            }
        },
        "2102": {
            "FirstName": "Max",
            "LastName": "Bar",
            "Classes": {
                "English": [1, 1],
                "Maths": [1, 2]
            }
        }
    }

    with open('school.json', 'w') as outfile:
        json.dump(school, outfile)

    with open('school.json') as json_file:
        school = json.load(json_file)

    mean_maths = aggregate_json(school, aggregate_function=statistics.mean, slice_scheme='[:][Classes][Maths]')
    mean_stud_maths = aggregate_json(school, aggregate_function=statistics.mean, slice_scheme='[2101][Classes][Maths]')
    mean_stud_classes = aggregate_json(school, aggregate_function=statistics.mean, slice_scheme='[2101][Classes][:]')
    mean_classes = aggregate_json(school, aggregate_function=statistics.mean, slice_scheme='[:][Classes][:]')

    print('mean for all students from Maths: {:.2f}'.format(mean_maths))
    print('mean for student with ID 2101 from Maths: {:.2f}'.format(mean_stud_maths))
    print('mean for student with ID 2101 across all classes: {:.2f}'.format(mean_stud_classes))
    print('mean for all students across all classes: {:.2f}'.format(mean_classes))

    arbitrary_example = {
        'firstA': {
            'secondA': 3,
            'secondB': 2
        },
        'firstB': {
            'secondA': 4,
            'secondB': [4, 1]
        }
    }
    print(
        'proof of reusability: '
        '[firstA][secondA] max: {}, [:][secondA] min: {}, [firstA][:] max: {}, [:][:] min: {}'.format(
            aggregate_json(arbitrary_example, aggregate_function=max, slice_scheme='[firstA][secondA]'),
            aggregate_json(arbitrary_example, aggregate_function=min, slice_scheme='[:][secondA]'),
            aggregate_json(arbitrary_example, aggregate_function=max, slice_scheme='[firstA][:]'),
            aggregate_json(arbitrary_example, aggregate_function=min, slice_scheme='[:][:]')
        )
    )
