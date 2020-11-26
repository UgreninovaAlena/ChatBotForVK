import datetime


class Result():

    def __init__(self, result, plase, massage, bool_result=0):
        self.time = str(datetime.datetime.now())
        self.error = result
        self.plase = plase
        self.massage = massage
        self.bool_result = bool_result

    def print_result(self):
        print(f'[{self.time}]   {self.plase}')
        print(f'Код выполнения [{self.error}] - {self.massage}')
        print()

    def result_to_str(self):
        line1 = (f'[{self.time}]   {self.plase}')
        line2 = (f'Код выполнения [{self.error}] - {self.massage}')
        return [line1, line2]


def catch_error(answer, JSONanswer, plase):
    if answer.status_code < 200 or answer.status_code > 299:
        return Result(1, plase, f'status_code = {answer.status_code} (< 200 or > 299)')
    if 'error' in JSONanswer.keys():
        return Result(1, plase, f'В ответе сервера получена ошибка: {JSONanswer["error"]["error_code"]} - {JSONanswer["error"]["error_msg"]}')
    return Result(0, plase, 'Запрос выполнен успешно')


