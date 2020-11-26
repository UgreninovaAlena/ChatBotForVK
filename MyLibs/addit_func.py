import json


def find_max_size(photo_size_list):
    photo_size_max = 0
    result_data = {}
    for photo in photo_size_list:
        pixel_count = photo['height'] * photo['width']
        if pixel_count > photo_size_max:
            photo_size_max = pixel_count
            result_data = photo
    return result_data


def get_input_data(filename):
    with open(filename) as f:
        result = json.load(f)
        result['app_id'] = int(result['app_id'])
    return result


def create_list_undefined_person(person_list):
    general_list = []

    for photo in photos:
        general_list.append(photo.link_photo)

    count_undef_photo = 3 - len(photos)
    while count_undef_photo > 0:
        general_list.append('https://sun9-39.userapi.com/ltx03LSdkFMbt7_HcV8kdCxmLpek4Lnc2qqm7w/2Pm8T6WbZ7Y.jpg')
        count_undef_photo = count_undef_photo - 1

    return general_list
