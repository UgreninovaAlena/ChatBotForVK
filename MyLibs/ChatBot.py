import vk_api
import random
from vk_api.longpoll import VkLongPoll, VkEventType
from mylibs import for_vk as mVK
from mylibs.for_database import add_user_in_DataBase, BASE, engine, DB_search_person, DB_add_person
from mylibs.addit_func import get_input_data


class BOT():

    message_dict = {'for_start': 'Я буду отправлять тебе фото людей, которые возможно заинтересуют тебя, а ты будешь отвечать мне, нравится тебе предложеный человек, или нет.\nЕсли ты готов, напиши мне в чате "start":)\nЕсли захочешь закончить диалог, напиши мне в чате "by"',
                    'input_age': 'Ведите возрастной промежуток для поиска в виде "[22-33]"',
                    'input_token': 'Ведите ваш токен в формате "token=XXXXXX...XXX":',
                    'start_search': 'Отлично! Для начала поиска введите "search":',
                    'for_one_VKPerson': 'Если вам нравится кондидат, введите "+", иначе введите "-":',
                    'send_set': 'Я нашла несколько хороших вариантов для тебя:)\nВведите "go" для продолжения',
                    'person_missed': 'Вы не сделали выбор:( \nНаверняка это нехороший человек! Отмеу его как неинтересного',
                    'person_interest_not': f'Пропускаем, не для нас :(',
                    'person_interest': f'Отличный выбор! Добавляем в рекомендации :)',
                    'all_person_is_viewed': 'Вау! Ты просмотрели всех возможных кондидатов!\n Заходи ко мне позже, и я поищу для тебя еще :)',
                    'search_started': 'Минутку, уже ищу...'
                    }

    def stoped_chat(self, event):
        self.write_msg(event.user_id, "Пока((")
        print('Бот остановлен')
        self.status_bot = 'stoped'

    def __init__(self, AOuthData):
        self.AOuthData = AOuthData
        self.vk = vk_api.VkApi(token=self.AOuthData['m_token'])
        self.longpoll = VkLongPoll(self.vk)
        self.status_bot = 'started'
        print('Бот запущен')

        BASE.metadata.create_all(engine)


    def write_msg(self, user_id, message, attachment = None, ranbom=None):
        if attachment == None:
            self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(10**7, 10**8)})
        else:
            self.vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(10**7, 10**8), "attachment": attachment})

    def send_set(self, event_user_id, person):
        attachment = []
        for photo in person.list_photos:
            attachment.append(f'photo{photo.id}')

        self.write_msg(event_user_id, '', ','.join(attachment))
        self.write_msg(event_user_id, f'{person.first_name} {person.last_name} \n{self.message_dict["for_one_VKPerson"]}')

    def chat(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:

                if event.to_me:
                    request = event.text.replace(' ', '').lower()

                    if request == "by":
                        # self.stoped_chat(event)
                        self.write_msg(event.user_id, "Пока((")
                        # return self.status_bot

                    elif request == "hi":
                        self.write_msg(event.user_id, f"{self.message_dict['for_start']}, {event.user_id}")
                                # Я буду отправлять тебе фото людей, которые возможно заинтересуют тебя, а ты будешь отвечать мне,
                                # нравится тебе предложеный человек, или нет. Если ты готов, напиши мне в чате "Старт"

                    elif request == "start":
                        self.write_msg(event.user_id, self.message_dict['input_token'])
                                # 'input_token': 'Ведите ваш токен в формате "token=XXXXXX...XXX":'}

                    elif request.find('token=') != -1:
                        self.token = request[6:]
                        self.write_msg(event.user_id, self.message_dict['input_age'])
                                # 'input_age': 'Ведите возрастной промежуток для поиска в виде "[22-33]:"'

                    elif request.find('[') != -1 and request.find('-') != -1 and request.find(']') != -1:
                        char = request.find('-')
                        self.age_from = int(request[1:char])
                        self.age_to = int(request[char+1:len(request)-1])
                        self.write_msg(event.user_id, self.message_dict['start_search'])
                                # 'start_search': 'Отлично! Для начала поиска введите "search"

                    elif request == "search":
                        self.user = mVK.User(event.user_id, self.token, self.age_from, self.age_to)
                        result = self.user.get_infouser()

                        if result.error == 1:
                            self.write_msg(event.user_id, result.massage)
                            self.stoped_chat(event)
                        else:
                            self.write_msg(event.user_id, self.message_dict['search_started'])
                                    # 'search_started': 'Минутку, уже ищу...'
                            result = add_user_in_DataBase(self.user)
                            VKpersons = mVK.VKperson()
                            result = VKpersons.get_people(self.user, 100, self.AOuthData, self.token)

                            if result.error == 1:
                                self.write_msg(event.user_id, result.massage)
                                self.stoped_chat(event)
                            else:
                                self.person_list_for_chat = []

                                for person in self.user.VKperson_list:
                                    if DB_search_person(self.user.id, person).bool_result == 0:
                                        photos = mVK.Photo()
                                        result = photos.get_photoslink(person, self.token)
                                        self.person_list_for_chat.append(person)

                                for elem in self.person_list_for_chat:
                                    elem.FOR_MY_print_elem()

                                if len(self.person_list_for_chat) == 0:
                                    self.write_msg(event.user_id, self.message_dict['all_person_is_viewed'])
                                            # 'all_person_is_viewed': 'Вау! Ты просмотрели всех возможных кондидатов! Заходи ко мне позже, и я поищу для тебя еще :)'
                                    self.stoped_chat(event)
                                else:
                                    self.current_person_index = -1
                                    self.write_msg(event.user_id, self.message_dict['send_set'])

                    elif request == "go":
                        self.current_person_index = self.current_person_index + 1
                        self.send_set(event.user_id, self.person_list_for_chat[self.current_person_index])

                    elif request == "+":
                        if self.current_person_index == len(self.person_list_for_chat)-1:
                            self.write_msg(event.user_id, self.message_dict['all_person_is_viewed'])
                                    # 'all_person_is_viewed': 'Вау! Ты просмотрели всех возможных кондидатов! Заходи ко мне позже, и я поищу для тебя еще :)'
                            self.stoped_chat(event)
                            # self.status_bot = 'stoped'
                        else:
                            self.person_list_for_chat[self.current_person_index].interest = True
                            DB_add_person(self.user.id, self.person_list_for_chat[self.current_person_index])
                            self.write_msg(event.user_id, self.message_dict['person_interest'])
                                    # 'person_interest': f'Отличный выбор! Добавляем в рекомендации :)'

                            self.current_person_index = self.current_person_index + 1
                            self.send_set(event.user_id, self.person_list_for_chat[self.current_person_index])

                    elif request == "-":
                        if self.current_person_index == len(self.person_list_for_chat)-1:
                            self.write_msg(event.user_id, self.message_dict['all_person_is_viewed'])
                                    # 'all_person_is_viewed': 'Вау! Ты просмотрели всех возможных кондидатов! Заходи ко мне позже, и я поищу для тебя еще :)'
                            self.stoped_chat(event)
                            # self.status_bot = 'stoped'
                        else:
                            self.person_list_for_chat[self.current_person_index].interest = False
                            DB_add_person(self.user.id, self.person_list_for_chat[self.current_person_index])
                            self.write_msg(event.user_id, self.message_dict['person_interest_not'])
                                    # 'person_interest_not': f'Пропускаем, не для нас :('

                            self.current_person_index = self.current_person_index + 1
                            self.send_set(event.user_id, self.person_list_for_chat[self.current_person_index])

                    else:
                        self.write_msg(event.user_id, "Я тебя не понимаю :(\n Попробуй, пожалуйта, еще раз")
