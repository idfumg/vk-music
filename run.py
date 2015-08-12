import requests
import json

from multiprocessing import Process, Queue
from os import path


EMAIL = 'email@gmail.com'
PASSWD = 'password'

PROCESSNUM = 3
DOWNLOAD_TRY_COUNT = 3
CHUNK_SIZE = 100000
DIRECTORY = '/home/idfumg/Downloads'

class VK(object):

    def __init__(self, email, passwd):
        self.email = email
        self.passwd = passwd
        self.session = requests.Session()

        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36'
        }

        self.session.headers.update(headers)

        self.login()

    def get(self, url):
        return self.session.get(url).text

    def post(self, url, data):
        return self.session.post(url, data=data)

    def login(self):
        data = {
            'act': 'login',
            'role': 'al_frame',
            'expire': '',
            'captcha_sid': '',
            'captcha_key': '',
            '_origin': 'http://vk.com',
            'ip_h': 'e6df45fef493bac900',
            'email': self.email,
            'pass': self.passwd
        }

        print self.post('https://login.vk.com?act=login', data).text

    def get_audio(self):
        data = {
            'act': 'load_audios_silent',
            'al': '1',
            'gid': '0',
            'please_dont_ddos': '2'
        }

        return self.post('https://vk.com/audio', data).text

def download_file_dummy(url, filename):
    print(filename)

    try:

        r = requests.get(url, stream=True) # download partially.

        size = int(r.headers['content-length'])

        if path.exists(filename) and path.getsize(filename) == size:
            return True

        with open(filename, 'wb') as fd:
            for buf in r.iter_content(CHUNK_SIZE):
                if not buf:
                    continue

                fd.write(buf)

    except (requests.exceptions.RequestException, FileNotFoundError):
        return False

    return True

def download_file(queue):
    mp3 = []

    while True:
        record = queue.get()

        if not record:
            break

        rc = False
        for i in range(DOWNLOAD_TRY_COUNT):
            rc = download_file_dummy(*record)
            if rc:
                break

        if not rc:
            print('Cant download:', record)
            mp3.append(record)

    if mp3:
        while True:
            print('Try to repeat download {} files...'.format(len(mp3)))
            for composition in mp3[:]:
                if download_file_dummy(*composition):
                    mp3.remove(composition)

def main():
    vk = VK(EMAIL, PASSWD)

    audios = vk.get_audio()
    print(audios)
    audios = audios[len('<!--17355<!>audio.css,audio.js<!>0<!>6614<!>0<!>'):]
    audios = audios.split('<!>')[0]
    audios = audios.replace('\'', '\"')
    print(audios)

if __name__ == '__main__':
    main()
