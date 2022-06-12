import json
import os
from itertools import count
from json import loads
from typing import Any

import requests
from requests import session


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


class MOS_API:
    def __init__(self, usr, pswd):
        self._usr: str | Any = usr
        self._pswd: str | Any = pswd
        self._session = session()
        self.auth()
        self.auth()

    def _ae(self):
        cookies = {
            'session-cookie': '16f79d85c38efc14ebdb8cb2beb261f5f93c0b34126b'
                              '45f77d023e4e59126f7d880a7e1576e3499916992ddae9983e60',
        }

        headers = {
            'authority': 'login.mos.ru',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'ru-RU,ru;q=0.9',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/102.0.0.0 Safari/537.36',
        }

        response = self._session.get(
            'https://login.mos.ru/sps/oauth/ae?scope=profile+openid+contacts+usr_grps&response_type=code&redirect_uri'
            '=https://www.mos.ru/api/acs/v1/login/satisfy&client_id=mos.ru',
            headers=headers, proxies=proxies, verify=False)
        return None

    def _first_request(self):
        pass

    def _default_request(self, url, advanced_headers=False):
        headers = {}
        if advanced_headers:  # Additional
            headers["Host"] = "login.mos.ru"
            headers["Accept-Language"] = "ru"
            headers["Accept-Encoding"] = "gzip, deflate, br"
            headers["Connection"] = "keep-alive"

        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        headers[
            "User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " \
                            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15"
        headers["Referer"] = "https://www.mos.ru/"
        response = self._session.get(url, headers=headers, allow_redirects=True, )
        return response

    def _login_post_request(self):
        url = "https://login.mos.ru/sps/login/methods/password?bo=/sps/oauth/ae?" \
              "scope=profile+openid+contacts+usr_grps&" \
              "response_type=code&" \
              "redirect_uri=https://www.mos.ru/api/acs/v1/login/satisfy&client_id=mos.ru"
        headers = {
            "Origin": "https://login.mos.ru", "Content-Type": "application/x-www-form-urlencoded",

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
        response = self._session.post(url, headers=headers, data=body_form, allow_redirects=True)

        return response

    def auth(self):
        fr = self._default_request(url="https://www.mos.ru/api/acs/v1/login?back_url=https://www.mos.ru/")
        if 307 not in (x.status_code for x in fr.history[0:1]):
            raise Exception("Церемония изменилась!")
        if 303 not in (x.status_code for x in fr.history[1:]):
            raise Exception("Церемония изменилась!")
        lr = self._login_post_request()

        '''cookies = {
            'fm': 'eyJtZXRob2RzIjpbInBhc3N3b3JkIiwieDUwOSIsImV4dGVybmFsSWRwczp2azp2a18xI'
                  'iwiZXh0ZXJuYWxJZHBzOmVzaWE6ZXNpYV8xIiwiZXh0ZXJuYWxJZHBzOm1haWw6bWFpbF8xIiwiZXh0ZXJu'
                  'YWxJZHBzOnNicmY6c2JyZl8xIiwiZXh0ZXJuYWxJZHBzOm9rOm9rXzEiLCJleHRlcm5hbElkcHM6eWFuZGV4OnlhbmR'
                  'leF8xIl0sInBhcmFtcyI6eyJjaGFsbGVuZ2UiOiJCbys2S01GOEJoV2pjckFXKzArQiIsImZ'
                  'lZFBvaW50cyI6InlhbmRleDp5YW5kZXhfMSJ9LCJmYXZvcml0ZU1ldGhvZHMiOltdfQ',
            'bua': '74842170-ae12-4f3e-b948-9cb6c9c2e852',
            'origin': 'mos.ru|%2Fsps%2Foauth%2Fae%3Fscope%3Dprofile%2Bopenid%2Bcontacts%2Busr_grps%26response_type'
                      '%3Dcode%26redirect_uri%3Dhttps%3A%2F%2Fwww.mos.ru%2Fapi%2Facs%2Fv1%2Flogin%2Fsatisfy'
                      '%26client_id%3Dmos.ru',
            'blg': 'ru',
            'oauth_az': '1N49xC53hXnLpk_HuCdfOcQIX_qu4qeLVvLEaw-0oqlroD5SK4S5EXiQCvTuCxqG'
                        '-mgxGQf3wNr5r2iCBnMTCFgiXY2cavyJaFWo7ltpN8Y',
            'blc': '6O0LXwfzyjWs02IJb--79Tq_hfCCfx_tHr2DnwdSojLNITRh64uQQ9DpliCaqEihojSlAu70zCavPkkg0KW28Zf2aRIARbqZ'
                   '-hur8UguFuQan7YH87OlA7Kgo-_cOlJKU2W8y3JEZ6'
                   '-sn7R2JxEg4GiUF1LiHKCN6uYYuriqNlMc9PgCp7SVDEVCGrUhsrWe95DgwS3PgY5wS9FIzkDBaIgXGfQuk6oBY'
                   '-rMwbd6OTRZupvPtsz0Uj7ioxK8HKVk_GEecKu3JtPVhuJqWpq9V_K7kNTntpMF8VgZqkLmMnnUY'
                   '-cRFva4kCkgEOoZtkmZxTvHLMw4S3gUVDkN_mknSPTpxgAdPiYDKDBcWccsPtYlpLiETaENk'
                   'YeX1UkO0bVhECGnK6Ty4ooHuOIxp31FVL_B1aT6JJaCYk7NWBji9lv42f7DldyB6BrJdg0m_edkUcqhO'
                   'zBzU9CZRl_3U5tumJzv5NouRXWjTqbraj4i3Uh7ymaUOyF_oUPRiBk1AbXnAuSJZb7mKuVa-v6iEg61j4PQ'
                   'ZPfCfSixsiRoWsGZ4WhTsCaKYIeOPE5c7UnhIikct1obQ--43yzmCla8tWK_-Vm3mk_Obhh50fDQxTaJm9Crm'
                   'jckCb9VtwDDMM3MaeBH|MTY1NDk1NTAxOA|U0gxQVMxMjhDQkM|AbsSEfExiJRoWtF4sCC_kA|5jZO'
                   '1kIFOhWCrX1nUEn5L1SQ25c',
            'mos_id': 'rBEAAmKknAYnZQCjpAiiAgA=',
            'session-cookie': '16f794d166c95cc4ebdb8cb2beb261f56619d1ff945ce6f1d86'
                              '7a8f270aaeac3f28f7847d13034a5375144262aa18ad1',
            '_ym_uid': '16549550151008434231',
            '_ym_d': '1654955015',
            '_ym_isad': '2',
            'KFP_DID': '0f7d2395-8012-8c7c-b0fc-33b57db3e5db',
            'oyystart': 'ff856417-cd2c-4178-af37-9b2ed4bd6388_0',
            'oxxfgh': '8ffefd79-8fe5-4eba-9870-2301b8402916#2#2592000000#5000#600000#81540',
        }

        headers = {
            'authority': 'login.mos.ru',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'ru-RU,ru;q=0.9',
            'cache-control': 'max-age=0',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://login.mos.ru',
            'referer': 'https://login.mos.ru/sps/login/methods/password?bo=%2Fsps%2Foauth%2Fae%3Fscope%3Dprofile'
                       '%2Bopenid%2Bcontacts%2Busr_grps%26response_type%3Dcode%26redirect_uri%3Dhttps%3A%2F%2Fwww.mos'
                       '.ru%2Fapi%2Facs%2Fv1%2Flogin%2Fsatisfy%26client_id%3Dmos.ru',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/102.0.0.0 Safari/537.36',
        }

        params = {
            'bo': '/sps/oauth/ae?scope=profile+openid+contacts+usr_grps&'
                  'response_type=code&'
                  'redirect_uri=https://www.mos.ru/api/acs/v1/login/satisfy&'
                  'client_id=mos.ru',
        }

        data = {
            'isDelayed': 'false',
            'login': #,
            'password': #,
            'bfp': BFP_BODY,
        }
        self._session.cookies.update({'oxxfgh': OXXFGH_COOKIE, 'oyystart': OYYSTART_COOKIE, 'KFP_DID': KFP_COOKIE})

        response1 = self._session.post('https://login.mos.ru/sps/login/methods/password', params=params,
                                       headers=headers, data=data, proxies=proxies, verify=False)
        # self._ae()
        '''
        return None

    def get_doctor_record(self):
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"102\", \"Google Chrome\";v=\"102\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-caller-id": "doctor-record::service"
        }
        url = "https://www.mos.ru/api/doctor-record/v1/doctors-schedule?omsNumber=7700005030524802&birthDate%5B0%5D" \
              "=2002-08-02&availableResourceId=19653741445 "

        headers = {
            "Host": "login.mos.ru",
            "Accept-Language": "ru",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            'authority': 'www.mos.ru',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6',
            'referer': 'https://www.mos.ru/services/zapis-k-vrachu/new/?omsNumber=7700005030524802&'
                       'birthDate=2002-08-02',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/102.0.0.0 Safari/537.36',
            'x-caller-id': 'doctor-record::service',
        }

        params = {
            'omsNumber': OMS_NUMBER,
            'birthDate[0]': BIRTH_DAY,
            'availableResourceId': '19653741445',
        }
        cookies = {
            'ACS-SESSID': 'kq17v4sensqh9848vlork7b1m4',
            'acst': 'v8s2SvXKmxzn7GlFkXHL_R8AevXqLpzzmsMtaNurZCBjODQxMmY5NC1jNjNkLTQ2NjgtODhiYy0xZTEzMDc5MGQ2ODM',
        }
        self._session.cookies.update(cookies)
        response = self._session.get('https://www.mos.ru/api/doctor-record/v1/doctors-schedule', params=params,
                                     headers=headers)
        if response.status_code == 200:
            lst = response.json()
            slots = lst['data']['list']
        return response


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    api = api_client(usr=USERNAME,
                     pswd=PASSWORD)
    api.get_doctor_record()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
