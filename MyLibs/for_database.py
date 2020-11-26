import sqlalchemy as sql
import psycopg2
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from mylibs.forlogs.Logger import get_log_to_file
from mylibs.result_creation import Result


DSN = 'postgres+psycopg2://test2:0****0@localhost:5432/test2'
BASE = declarative_base()
engine = sql.create_engine(DSN)
Session = sessionmaker(bind=engine)
session = Session()


class users(BASE):
    __tablename__ = 'users'

    id = sql.Column(sql.Integer, primary_key = True)#Имеем в виду то, что ид в базе данных = ид в вк

    first_name = sql.Column(sql.String)
    last_name = sql.Column(sql.String)
    sex = sql.Column(sql.Integer)
    country_code = sql.Column(sql.Integer)
    city_code = sql.Column(sql.Integer)


    age = sql.Column(sql.Integer)
    range_age = sql.Column(sql.String)

    dating_users = relationship('datinguser', backref = 'user')


class datinguser(BASE):
    __tablename__ = 'datinguser'

    id = sql.Column(sql.Integer, primary_key=True)

    first_name = sql.Column(sql.String)
    last_name = sql.Column(sql.String)
    age = sql.Column(sql.Integer)
    interest = sql.Column(sql.Boolean)

    id_user = sql.Column(sql.Integer, sql.ForeignKey('users.id'))
    id_photos = relationship('photos', backref = 'datingUser')


class photos(BASE):
    __tablename__ = 'photos'

    # id = sql.Column(sql.Integer, primary_key=True)--------------------------------------------------------------------
    id = sql.Column(sql.String, primary_key=True)
    link = sql.Column(sql.String)
    count_likes = sql.Column(sql.Integer)

    id_datinguser = sql.Column(sql.Integer, sql.ForeignKey('datinguser.id'))


@get_log_to_file('Databaselog.txt')
def add_user_in_DataBase(VKuser):
    DBuser = Session().query(users).filter(users.id==VKuser.id).first()

    if DBuser == None:
        DBuser = users(id=VKuser.id, first_name=VKuser.firs_name, last_name=VKuser.last_name, sex=VKuser.sex,
                      country_code=VKuser.country_code['id'], city_code = VKuser.city_code['id'], age=VKuser.age,
                      range_age=f'[{VKuser.age_from}-{VKuser.age_to}')

        session.add(DBuser)
        session.commit()

        return Result(0, f'Получение информации о пользователе {VKuser.id} из базы данных', 'Пользователь добавлен в БД')
    else:
        return Result(0, f'Получение информации о пользователе {VKuser.id} из базы данных', 'Пользователь найден в БД')


@get_log_to_file('Databaselog.txt')
def DB_search_person(VKuser_id, VKperson):
    DBperson = Session().query(datinguser).filter(datinguser.id == VKperson.id, datinguser.id_user == VKuser_id).first()
    if DBperson == None:
        return Result(0, f'Поиск персоны {VKperson.id} в базе данных', 'Нет информации', 0)
    else:
        return Result(0, f'Поиск персоны {VKperson.id} в базе данных', 'Информация найдена', 1)


@get_log_to_file('Databaselog.txt')
def DB_add_person(VKuser_id, VKperson):
    StrResult_forperson = f'\n    Персона {VKperson.id}: данные загружены в БД'
    ListResult_forphotos = []

    DBperson = datinguser(id=VKperson.id, first_name=VKperson.first_name, last_name=VKperson.last_name, age=VKperson.age, id_user=VKuser_id, interest=VKperson.interest)
    session.add(DBperson)
    session.commit()

    DBlist_photos = []
    for VKphoto in VKperson.list_photos:
        DBphoto = Session().query(photos).filter(photos.id == VKphoto.id).first()
        if DBphoto == None:
            DBphoto = photos(id=VKphoto.id, link=VKphoto.link_photo, count_likes=VKphoto.likes, id_datinguser=VKperson.id)
            session.add(DBphoto)
            session.commit()

            StrResult_forphotos = f'\n        Фото {VKphoto.id}: Загружено в бд'
            ListResult_forphotos.append(StrResult_forphotos)
        else:
            StrResult_forphotos = f'\n        Фото {VKphoto.id}: уже есть в бд\n'
            ListResult_forphotos.append(StrResult_forphotos)

        str_for_result = 'Информация загружена в БД' + StrResult_forperson + ''.join(ListResult_forphotos)
    return Result(0, f'Загрузка данных DatingUser {VKperson.id}, Photos в БД', str_for_result)