import os
import pickle
from functools import wraps
from itertools import count
from typing import Any, List, Callable

from decohints import decohints
from requests import session, Response
from overloading import overload


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


def api_client(usr, pswd):
    return MOS_API(usr, pswd)


USERNAME = os.environ['username']  # example@email.com
PASSWORD = os.environ['password']
OMS_NUMBER = os.environ['oms_number']  # A lot of numbers
BIRTH_DAY = os.environ['birth_day']  # 2001-02-29
http_proxy = "http://192.168.0.198:5555"  # TEST_PROXY
proxies = {
    "http": http_proxy,
    "https": http_proxy,
    "ftp": http_proxy
}
proxies.clear()
# Thanks to https://github.com/Lesterrry/mosru/blob/master/lib/mosru/auth.rb
# I have no idea how to fetch these values so let's hope they will remain the same
OXXFGH_COOKIE = "8ffefd79-8fe5-4eba-9870-2301b8402916#2#2592000000#5000#600000#81540"
OYYSTART_COOKIE = "8ffefd79-8fe5-4eba-9870-2301b8402916_1"
BFP_BODY = "e4eb7b3d199624ca9b36750e9e0f3404"
KFP_COOKIE = "72b01986-3f1e-4bfa-ccf3-07a1b721f1bc"


class ScheduleOfDoctor:
    def __init__(self, json: dict | Any):
        """
        Распаковка json
        :param json:
        """
        self._json = json
        days = json.get('list', [])

        pass


class PlannedSignByDoctorDayTime:
    def __init__(self, doctor_name: str, day, time):
        self._preffered_doctor_name = doctor_name
        self._preffered_day = day
        self._preffered_time = time

    @property
    def doctor_name(self):
        return self._preffered_doctor_name

    @property
    def day(self):
        return self._preffered_day

    @property
    def day_time(self):
        return self._preffered_time


class Doctor:
    @overload
    def __init__(self, id: int):
        self._id = id

    @overload
    def __init__(self, id: int, name: str):
        self.__init__(id)
        self._name = name

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name



class VariantSign:
    def __init__(self, doctor, date):
        self._doctor = doctor
        self._date = date

    @property
    def doctor(self):
        return self._doctor

    @property
    def date(self):
        return self._date


class MOS_API:
    _DEFAULT_HEADERS = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
        "Referer": "https://www.mos.ru/"
    }

    @property
    def authentificated(self) -> bool:
        return self._authentificated

    def __init__(self, usr, pswd):
        self._usr: str | Any = usr
        self._pswd: str | Any = pswd
        self._session = session()
        with open("cookies", "rb") as f:
            self._session.cookies.update(pickle.load(f))
        self._authentificated = self.auth()

    def _default_request(self, url, advanced_headers=False):
        headers = {}
        headers.update(self._DEFAULT_HEADERS)
        if advanced_headers:  # Additional
            headers["Host"] = "login.mos.ru"
            headers["Accept-Language"] = "ru"
            headers["Accept-Encoding"] = "gzip, deflate, br"
            headers["Connection"] = "keep-alive"
        response = self._session.get(url, headers=headers, allow_redirects=False, proxies=proxies, verify=False)
        return response

    def _login_post_request(self):
        url = "https://login.mos.ru/sps/login/methods/password?bo=/sps/oauth/ae?" \
              "scope=profile+openid+contacts+usr_grps&" \
              "response_type=code&" \
              "redirect_uri=https://www.mos.ru/api/acs/v1/login/satisfy&client_id=mos.ru"
        headers = {
            "Origin": "https://login.mos.ru",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",

            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",

            "Referer": "https://login.mos.ru/sps/login/methods/password?bo=/sps/oauth/ae?"
                       "scope=profile+openid+contacts+usr_grps&"
                       "response_type=code&"
                       "redirect_uri=https://www.mos.ru/api/acs/v1/login/satisfy&"
                       "client_id=mos.ru"
        }

        # headers["Cookie"] = cookie_jar.plain + "; #{OXXFGH_COOKIE}; #{OYYSTART_COOKIE};"
        self._session.cookies.update({'oxxfgh': OXXFGH_COOKIE, 'oyystart': OYYSTART_COOKIE, 'KFP_DID': KFP_COOKIE})
        body_form = {
            'isDelayed': 'false',
            'login': USERNAME,
            'password': PASSWORD,
            'bfp': BFP_BODY,
        }
        response = self._session.post(url, headers=headers, data=body_form, allow_redirects=True, proxies=proxies,
                                      verify=False, cookies=self._session.cookies)

        return response

    def auth(self):
        try:
            test_auth_response = self._session.get('https://www.mos.ru/api/doctor-record/v1/doctors-schedule',
                                                   headers=self._DEFAULT_HEADERS, proxies=proxies, verify=False)
            if test_auth_response.status_code == 400:
                return True

            welcome_response = self._default_request(url="https://www.mos.ru/api/acs/v1/login?"
                                                         "back_url=https://www.mos.ru/")
            if welcome_response.status_code != 307:
                raise Exception("Церемония изменилась!")
            welcome_response_iteration = welcome_response
            for tries in count():
                if tries >= 3:
                    raise Exception("Церемония изменилась!")
                location = welcome_response_iteration.headers['location']
                if location[0] == '/':
                    location = "https://login.mos.ru" + location

                welcome_response_iteration = self._default_request(url=location, advanced_headers=True)
                if welcome_response_iteration.status_code != 303:
                    break
            login_response = self._login_post_request()
            login_response_history: List[Response] = login_response.history + [login_response]
            if 302 not in map(lambda x: x.status_code, login_response_history):
                raise Exception("Церемония изменилась!")
            with open("cookies", "wb") as f:
                pickle.dump(self._session.cookies, f)
        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    @decohints
    def _provide_authorized(func: Callable):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not self._authentificated:
                if not self.auth():
                    raise Exception("Не авторизован")
            func(self, *args, **kwargs)

        return wrapper

    @_provide_authorized
    def get_doctor_record(self):
        headers = self._DEFAULT_HEADERS
        doctor_id = 19653741445
        params = {
            'omsNumber': OMS_NUMBER,
            'birthDate[0]': BIRTH_DAY,
            'availableResourceId': doctor_id,
        }
        response = self._session.get('https://www.mos.ru/api/doctor-record/v1/doctors-schedule', params=params,
                                     headers=headers, proxies=proxies, verify=False)
        if response.status_code == 200:
            lst: dict | Any = response.json()
            if lst.get('code', '').lower() != 'success':
                raise Exception("Церемония изменилась!")
            slots: list | Any = lst['data']['list']
            doctor = Doctor()
            schedule = ScheduleOfDoctor(json=lst['data'])
        return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    api = api_client(usr=USERNAME,
                     pswd=PASSWORD)
    if api.authentificated:
        api.get_doctor_record()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
