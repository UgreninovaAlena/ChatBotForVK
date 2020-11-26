import random
import requests
from urllib.parse import urlencode
from MyLibs.Iteratirs import GetlinkForPhotos, ListIteration
from MyLibs.LibAdditionalFunction import get_input_data
from MyLibs.ForLogs.Logger import get_log_to_file
from MyLibs.ResultCreation import catch_error
from datetime import date

AOuthData = get_input_data("Data.txt")


class User():

    def __init__(self, user_id, token, age_from = 18, age_to = 50):
        self.age_from = age_from
        self.age_to = age_to
        self.token = token
        self.id = user_id

    def init_user(self, infodict):
        # self.id = infodict['id']
        self.firs_name = infodict['first_name']
        self.last_name = infodict['last_name']
        self.sex = infodict['sex']
        self.country_code = infodict['country']
        self.city_code = infodict['city']

        born_date = list(map(int, infodict['bdate'].split('.')))
        today = date.today()
        self.age = today.year - born_date[2] - ((today.month, today.day) < (born_date[1], born_date[0]))

        self.VKperson_list = []

    @get_log_to_file('VKlog.txt')
    def get_infouser(self):
        URL_to_get_userinfo = 'https://api.vk.com/method/users.get'
        parameters_to_get_userinfo = {'fields': 'first_name, last_name, bdate, country, city, sex',
                                      'user_ids': self.id,
                                      'access_token': self.token,
                                      'v': 5.89
                                      }

        answer = requests.get(url=URL_to_get_userinfo, params=parameters_to_get_userinfo)
        JSONanswer = answer.json()
        result = catch_error(answer, JSONanswer, f'Отправка запроса для получения информации о пользователе {self.id}')
        if result.error == 1:
            return result
        list_info = JSONanswer['response'][0]
        self.user = self.init_user(list_info)
        return result


class VKperson():

    def init_VKperson(self, VKperson_infolist):
        self.id = VKperson_infolist['id']
        self.first_name = VKperson_infolist['first_name']
        self.last_name = VKperson_infolist['last_name']
        if 'age' in VKperson_infolist.keys():
            born_date = list(map(int, VKperson_infolist['bdate'].split('.')))
            today = date.today()
            self.age = today.year - born_date[2] - ((today.month, today.day) < (born_date[1], born_date[0]))
        else:
            self.age = None
        self.interest = None
        self.sex = VKperson_infolist['sex']
        self.list_photos = []

    @get_log_to_file('VKlog.txt')
    def get_people(self, user, count_set, AOuthData, token):
        self.URL_to_search = 'https://api.vk.com/method/users.search'
        self.user_token = token

        sex = 1
        if user.sex == 1:
            sex = 2

        self.parametrs_to_search = {
            'user_ids': AOuthData['app_id'],
            'access_token': self.user_token,
            'has_photo' : True,
            'sex': sex,
            'age_from': user.age_from,
            'age_to': user.age_to,
            'country': user.country_code['id'],
            'city': user.city_code['id'],
            'sort': 0,
            'count': count_set,
            'status': 6,
            'fields': 'photo_id, country, city, sex, deactivated, is_closed',
                                   #deactivated = содержит значение deleted или banned.
            'v': 5.89
        }
        answer = requests.get(url=self.URL_to_search, params=self.parametrs_to_search)
        JSONanswer = answer.json()

        result = catch_error(answer, JSONanswer, 'Отправка запроса для поиска персоны')
        if result.error == 1:
            return result

        list_info = JSONanswer['response']['items']
        for elem in ListIteration(list_info):
            if elem['can_access_closed'] != False:
                person = VKperson()
                person.init_VKperson(elem)
                user.VKperson_list.append(person)

        return result


class Photo():

    def init_photo(self, Photos_infolist):
        self.owner_id = Photos_infolist['owner_id']
        self.id = f"{str(self.owner_id)}_{Photos_infolist['id']}"
        self.link_photo = Photos_infolist['link']['url']
        self.likes = Photos_infolist['likes']

    @get_log_to_file('VKlog.txt')
    def get_photoslink(self, VKperson, token):
        URL_for_get_photos = 'https://api.vk.com/method/photos.get'
        parameters_for_photos_get = {
            'lang': 0,
            'owner_id': '',
            'album_id': 'profile',
            'extended': 1,
            'feed_type': 'photo',
            'photo_sizes': 1,
            'count': 1000,
            'access_token': token,
            'v': 5.89
        }
        parameters_for_photos_get['owner_id'] = VKperson.id

        answer = requests.get(url = URL_for_get_photos, params = parameters_for_photos_get)
        JSONanswer = answer.json()

        result = catch_error(answer, JSONanswer, f'Отправка запроса для получения ссылок для фотографий (Персона {VKperson.id})')
        if result.error == 1:
            return result

        list_photos_link = JSONanswer['response']['items']
        for x in GetlinkForPhotos(list_photos_link, VKperson.id):
            elem_for_phoyolinks_array = Photo()
            if x['link'] !={}:
                elem_for_phoyolinks_array.init_photo(x)
                VKperson.list_photos.append(elem_for_phoyolinks_array)

        return result


def write_msg(vk, user_id, message, attachment = None):
    if attachment == None:
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(10**7, 10**8)})
    else:
        vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(10**7, 10**8), "attachment": attachment})


def send_set(vk, user_id, person):

    message = 'Если вам нравится кондидат, введите "+", иначе введите "-":',
    attachment = []
    for photo in person.list_photos:
        attachment.append(f'photo{photo.id}')

    write_msg(vk, user_id, '', ','.join(attachment))
    write_msg(vk, user_id, f'{person.first_name} {person.last_name} \n{message}')


def autorize():
    TOKEN_GRUPPI = 'b1d305822a69df00ac8e9efd6e9ad7324e2685653dadeba08dd7cafb146ab402756a8bfab290de49d9de3'
    URL_for_autorize = 'https://oauth.vk.com/authorize'
    ID = 7659856
    parameters_for_autorize = {
        'client_id': 7659856,
        'redirect_uri': 'https://oauth.vk.com/blank.html',
        'display': 'popup',
        'scope': 'notify, photos, stories, pages, status, notes, messages, ads, docs, groups, notifications, stats, email, market',
        'response_type': 'token',
        'v': 5.89
            }
    print('?'.join((URL_for_autorize, urlencode(parameters_for_autorize))))