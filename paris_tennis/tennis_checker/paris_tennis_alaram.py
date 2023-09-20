from datetime import datetime
from typing import Union, List
import requests
from json import dumps, loads
from pprint import pprint


class CheckAvailableCourts:
    def __init__(self,
                 alarm_date_time: datetime,
                 court_names: Union[str, List[str]]):
        self.alarm_date_time = alarm_date_time

        self.court_names = court_names
        self.cookies = None

    def set_cookie(self):
        url = """https://tennis.paris.fr"""
        response = requests.get(url=url)
        self.cookies = response.cookies
        return self.cookies

    def get_available(self):
        url = """https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&action=rechercher_creneau"""
        payload = """hourRange=8-22&when=20%2F09%2F2023&
        selWhereTennisName=Elisabeth&selInOut%5B%5D=V&selInOut%5B%5D=F&selCoating%5B%5D=96&selCoating%5B%5D=2095&selCoating%5B%5D=94&selCoating%5B%5D=1324&selCoating%5B%5D=2016&selCoating%5B%5D=92"""
        response = requests.get(url=url,
                                cookies=self.cookies,
                                data=payload)

        tennis = response.text.split("var tennis =")[-1]
        tennis = tennis.split("	var markers = {};")[0]
        tennis = tennis.strip()

        tennis = tennis.rstrip(";\r\n\t\r\n\t")

        tennis = loads(tennis)

        print(tennis)

        print(type(tennis))
        for index, value in tennis:
            print(value)


if __name__ == '__main__':
    check_courts = CheckAvailableCourts(alarm_date_time=datetime(2023, 9, 20),
                                        court_names=['elisabeth'])
    check_courts.get_available()
