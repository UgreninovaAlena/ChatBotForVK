from urllib.parse import urlencode

from MyLibs.MS import work
from MyLibs.LibAdditionalFunction import get_input_data

if __name__ == '__main__':

    URL_for_autorize = 'https://oauth.vk.com/authorize'
    ID = 7656145
    param = {
        'client_id': ID,
        'display': 'popup',
        'scope': 'photos, status',
        'response_type': 'token',
        'v': 5.89}
    url = '?'.join((URL_for_autorize, urlencode(param)))
    print(url)

    AOuthData = get_input_data("Data.txt")
    work(AOuthData)

    # AOuthData = get_input_data("Data.txt")
    # a = BOT(AOuthData)
    # a.chat()
