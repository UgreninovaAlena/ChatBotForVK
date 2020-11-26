import random
from vk_api import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

import mylibs.for_database as MyDB
import mylibs.for_vk as MyVK
from mylibs.addit_func import get_input_data


class SM:

    message_dict = {'start': 'Я буду отправлять тебе фото людей, которые возможно заинтересуют тебя, а ты будешь отвечать мне, нравится тебе предложеный человек, или нет.\nЕсли ты готов, напиши мне в чате "start":)\nЕсли захочешь закончить диалог, напиши мне в чате "by"',
        'input_age_from': 'Ведите нижнюю границу возрастного промежутка для поиска:',
        'input_age_to': 'Ведите верхнюю границу возрастного промежутка для поиска:',
        'input_token': 'Ведите ваш токен в формате "token=XXXXXX...XXX":',
        'repeat_input': "Я тебя не понимаю :(\n Попробуй, пожалуйта, еще раз",
        'stop': 'Пока :(\n Если захочешь продолжить, пиши мне "hi"',
        'start_search': 'Отлично! Для начала поиска введите "search":',
        'send_set': 'Я нашла несколько хороших вариантов для тебя:)\nВведите "go" для продолжения',
        'person_interest_not': f'Пропускаем, не для нас :(',
        'person_interest': f'Отличный выбор! Добавляем в рекомендации :)',
        'all_person_is_viewed': 'Вау! Ты просмотрели всех возможных кондидатов!\n Заходи ко мне позже, и я поищу для тебя еще :)',
        'search_started': 'Минутку, уже ищу...'}

    def __init__(self, vk, curent_status, AOuthData):
        self.vk = vk
        self.change_current_status(curent_status)
        self.AOuthData = AOuthData

    def update_massage(self, event):
        self.event = event
        self.request = self.event.text.replace(' ', '').lower()

    def change_current_status(self, new_status, additional_message = None):
        self.current_status = new_status
        if new_status != 'start':
            message = self.message_dict[new_status]
            MyVK.write_msg(self.vk, self.event.user_id, message)
            if additional_message != None:
                MyVK.write_msg(self.vk, self.event.user_id, additional_message)


    def act_repeat_input(self):
        MyVK.write_msg(self.vk, self.event.user_id, self.message_dict['repeat_input'])
        self.change_current_status(self.current_status)

    def act_start(self):
        if self.request == "start" or self.request == 'hi':
            self.change_current_status('input_token')

        elif self.request == 'by':
            self.act_stop()

        else:
            self._repeat_input()

    def act_stop(self, additional_message = None):
        self.change_current_status('stop', additional_message)

    def act_input_token(self):
        if self.request.find('token=') != -1:
            self.token = self.request[6:]
            self.change_current_status('input_age_from')

        elif self.request == 'by':
            self.act_stop()

        else:
            self._repeat_input()

    def act_input_age_from(self):
        if self.request.isdigit() == 1:
            self.age_from = int(self.request)
            self.change_current_status('input_age_to')

        elif self.request == 'by':
            self.act_stop()

        else:
            self._repeat_input()

    def act_input_age_to(self):
        if self.request.isdigit() and self.age_from <= int(self.request):
            self.age_to = int(self.request)
            self.change_current_status('start_search')

        elif self.request == 'by':
            self.act_stop()

        elif self.age_from > int(self.request):
            error_str = f'Вы ввели некорректный промежуток возраста. Попробуйте еще раз'
            MyVK.write_msg(self.vk, self.event.user_id, error_str)
            self.change_current_status('input_age_from')

    def act_start_search(self):
        if self.request == 'search':
            self.user = MyVK.User(self.event.user_id, self.token, self.age_from, self.age_to)
            result = self.user.get_infouser()

            if result.error == 1:
                # MyVK.write_msg(self.vk, self.event.user_id, result.massage)
                self.change_current_status('input_token', result.massage)
            else:
                MyVK.write_msg(self.vk, self.event.user_id, self.message_dict['search_started'])
                result = MyDB.add_user_in_DataBase(self.user)
                VKpersons = MyVK.VKperson()
                result = VKpersons.get_people(self.user, 100, self.AOuthData, self.token)

                if result.error == 1:
                    # MyVK.write_msg(self.vk, self.event.user_id, result.massage)
                    self.change_current_status('stop', result.massage)
                else:
                    self.person_list_for_chat = []

                    for person in self.user.VKperson_list:
                        if MyDB.DB_search_person(self.user.id, person).bool_result == 0:
                            photos = MyVK.Photo()
                            result = photos.get_photoslink(person, self.token)
                            self.person_list_for_chat.append(person)

                    if len(self.person_list_for_chat) == 0:
                        self.change_current_status('stop', self.message_dict['all_person_is_viewed'])
                    else:
                        self.current_person_index = -1
                        self.change_current_status('send_set')

        elif self.request == 'by':
            self.change_current_status('stop')

        else:
            self._repeat_input()

    def act_send_set(self):
        if self.request == "go":
            self.current_person_index = self.current_person_index + 1
            MyVK.send_set(self.vk, self.event.user_id, self.person_list_for_chat[self.current_person_index])

        elif self.request == "+":
            if self.current_person_index == len(self.person_list_for_chat) - 1:
                self.change_current_status('stop', self.message_dict['all_person_is_viewed'])
            else:
                self.person_list_for_chat[self.current_person_index].interest = True
                MyDB.DB_add_person(self.user.id, self.person_list_for_chat[self.current_person_index])
                MyVK.write_msg(self.vk, self.event.user_id, self.message_dict['person_interest'])

                self.current_person_index = self.current_person_index + 1
                MyVK.send_set(self.vk, self.event.user_id, self.person_list_for_chat[self.current_person_index])

        elif self.request == "-":
            if self.current_person_index == len(self.person_list_for_chat) - 1:
                self.change_current_status('stop', self.message_dict['all_person_is_viewed'])
            else:
                self.person_list_for_chat[self.current_person_index].interest = False
                MyDB.DB_add_person(self.user.id, self.person_list_for_chat[self.current_person_index])
                MyVK.write_msg(self.vk, self.event.user_id, self.message_dict['person_interest_not'])

                self.current_person_index = self.current_person_index + 1
                MyVK.send_set(self.vk, self.event.user_id, self.person_list_for_chat[self.current_person_index])

        elif self.request == 'by':
            self.change_current_status('stop')

        else:
            self._repeat_input()


    def process_message(self):
        if self.current_status == 'start':
            self.act_start()

        elif self.current_status == 'input_token':
            self.act_input_token()

        elif self.current_status == 'input_age_from':
            self.act_input_age_from()

        elif self.current_status == 'input_age_to':
            self.act_input_age_to()

        elif self.current_status == 'start_search':
            self.act_start_search()

        elif self.current_status == 'send_set':
            self.act_send_set()

        else:
            self.act_start()


def work(AOuthData):
    vk = vk_api.VkApi(token=AOuthData['m_token'])
    longpoll = VkLongPoll(vk)
    curent_status = 'start'
    first_massage = 1

    iteration = SM(vk, curent_status, AOuthData)

    for event in longpoll.listen():
        if first_massage == 1:
            MyVK.write_msg(vk, event.user_id, f"{iteration.message_dict['start']}, {event.user_id}")
            first_massage = 0

        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                iteration.update_massage(event)
                iteration.process_message()
                curent_status = iteration.current_status