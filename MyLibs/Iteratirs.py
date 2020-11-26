from mylibs.for_database import Session, datinguser
from mylibs.addit_func import find_max_size


class GetlinkForPhotos():

    def __init__(self, list_photos_link, VKperson_id):
        self.cuernt_index = 2
        self.index = -1
        self.list_photos_link = list_photos_link
        self.result_list = list_photos_link[0:3]
        self.VKperson_id = VKperson_id

    def __iter__(self):
        return self

    def find_list(self):
        if len(self.list_photos_link) < 3:
            self.result_list = self.list_photos_link
        else:
            self.cuernt_index = self.cuernt_index + 1

            while self.cuernt_index < len(self.list_photos_link):
                curent_elem = self.list_photos_link[self.cuernt_index]
                if curent_elem['likes']['count'] > self.result_list[0]['likes']['count']:
                    self.result_list[0] = curent_elem
                else:
                    if curent_elem['likes']['count'] > self.result_list[1]['likes']['count']:
                        self.result_list[1] = curent_elem
                    else:
                        if curent_elem['likes']['count'] > self.result_list[2]['likes']['count']:
                            self.result_list[2] = curent_elem

                self.cuernt_index = self.cuernt_index + 1

    def __next__(self):
        self.find_list()
        self.index = self.index + 1

        while self.index < len(self.result_list):
            result_elem = {}
            result_elem['id'] = self.result_list[self.index]['id']
            result_elem['owner_id'] = self.result_list[self.index]['owner_id']
            result_elem['link'] = find_max_size(self.result_list[self.index]['sizes'])
            result_elem['likes'] = self.result_list[self.index]['likes']['count']
            return result_elem

        if self.index == 3:
            raise StopIteration
        raise StopIteration


class ListIteration():

    def __init__(self, list):
        self.list = list
        self.curent_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        while self.curent_index < len(self.list) -1:
            self.curent_index = self.curent_index+1

            return self.list[self.curent_index]

        raise StopIteration


class ListPersonForChat():

    def __init__(self, VKperson_list, user_id):
        self.VKperson_list = VKperson_list
        self.user_id = user_id

        self.result_list = []
        self.curent_index = -1

    def __iter__(self):
        return self

    def __next__(self):
        while self.curent_index < len(self.VKperson_list) - 1:
            self.curent_index = self.curent_index + 1
            DBperson = Session().query(datinguser).filter(datinguser.id == self.VKperson_list[self.curent_index].id,
                                                              datinguser.id_user == self.user_id).first()
            if DBperson == None:
                return self.VKperson_list[self.curent_index]

        raise StopIteration


