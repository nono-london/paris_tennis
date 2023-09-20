from datetime import datetime
from typing import Union, List
import requests
from json import dumps, loads
from pprint import pprint
from dataclasses import dataclass
from typing import Union, Optional, List, Dict
from paris_tennis.tennis_checker.paris_tennis_class import ParisTennis


class CheckAvailableCourts(ParisTennis):
    def __init__(self,
                 alarm_date_time: datetime,
                 court_names: Union[str, List[str]]):
        self.alarm_date_time = alarm_date_time

        self.court_names = court_names
        self.cookies = None
        self.indoor: bool = False

    def set_cookie(self):
        url = """https://tennis.paris.fr"""
        response = requests.get(url=url)
        self.cookies = response.cookies
        return self.cookies

    def _check_indoor(self, court_number: str,
                      list_of_courts: List[Dict]):
        for court in list_of_courts:
            if court.get('_airNom') == court_number:
                return court.get('_airCvt') == "V"

        return False

    def get_available(self, trade_date: datetime):
        url = """https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&action=rechercher_creneau"""
        trade_day = trade_date.strftime("%d")
        trade_month = trade_date.strftime("%m")
        trade_year = trade_date.strftime("%Y")
        payload = f"""hourRange=8-22&when={trade_day}%2F{trade_month}%2F{trade_year}&
        selWhereTennisName=Elisabeth&selInOut%5B%5D=V&selInOut%5B%5D=F&selCoating%5B%5D=96&selCoating%5B%5D=2095&selCoating%5B%5D=94&selCoating%5B%5D=1324&selCoating%5B%5D=2016&selCoating%5B%5D=92"""
        response = requests.get(url=url,
                                cookies=self.cookies,
                                data=payload)

        tennis = response.text.split("var tennis =")[-1]
        tennis = tennis.split("	var markers = {};")[0]
        tennis = tennis.strip()

        tennis = tennis.rstrip(";\r\n\t\r\n\t")

        tennis = loads(tennis)

        for tenni in tennis['features']:
            if tenni.get('properties').get('general').get('_codePostal') == '75014':
                tenni.get('properties').get('courts').get('_airCvt')
                print(self.set_indoor(indoor_data=tenni.get('_airCvt')))
                print(self.set_court_number(court_number=tenni.get('_airNom')))


if __name__ == '__main__':
    check_courts = CheckAvailableCourts(alarm_date_time=datetime(2023, 9, 21),
                                        court_names=['atlantique'])
    check_courts.get_available(trade_date=datetime(2023, 9, 21))
