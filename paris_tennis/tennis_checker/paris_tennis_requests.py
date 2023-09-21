from datetime import datetime
from typing import Union, List
import requests
from json import dumps, loads
from pprint import pprint
from dataclasses import dataclass
from typing import Union, Optional, List, Dict
from paris_tennis.tennis_checker.paris_tennis_class import ParisTennis, TennisCourt


class CheckAvailableCourts(ParisTennis):
    def __init__(self,
                 alarm_date_time: datetime,
                 court_names: Union[str, List[str]]):
        self.alarm_date_time = alarm_date_time

        self.court_names = court_names
        self.cookies = None
        self.indoor: bool = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/101.0.0.0'}

    def set_cookie(self):
        url = """https://tennis.paris.fr"""
        response = requests.get(url=url, headers=self.headers)
        self.cookies = response.cookies
        return self.cookies

    def _check_indoor(self, court_number: str,
                      list_of_courts: List[Dict]):
        for court in list_of_courts:
            if court.get('_airNom') == court_number:
                return court.get('_airCvt') == "V"

        return False

    def get_available(self, trade_date: datetime,
                      tennis_names: Optional[List[str]] = None):
        if not tennis_names:
            tennis_names = ['Elisabeth', 'Atlantique']
        url = """https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&action=rechercher_creneau"""
        trade_day = trade_date.strftime("%d")
        trade_month = trade_date.strftime("%m")
        trade_year = trade_date.strftime("%Y")
        payload = f"""hourRange=8-22&when={trade_day}%2F{trade_month}%2F{trade_year}&
        selWhereTennisName={tennis_names[0]}&selInOut%5B%5D=V&selInOut%5B%5D=F&selCoating%5B%5D=96&selCoating%5B%5D=2095&selCoating%5B%5D=94&selCoating%5B%5D=1324&selCoating%5B%5D=2016&selCoating%5B%5D=92"""
        response = requests.get(url=url,
                                cookies=self.set_cookie(),
                                data=payload)

        tennis = response.text.split("var tennis =")[-1]
        tennis = tennis.split("	var markers = {};")[0]
        tennis = tennis.strip()

        tennis = tennis.rstrip(";\r\n\t\r\n\t")

        tennises = loads(tennis)
        results: List[ParisTennis] = []
        for tennis in tennises['features']:
            if tennis['properties']['general']['_nomSrtm'] in tennis_names:
                paris_tennis = ParisTennis()
                paris_tennis.name = tennis['properties']['general']['_nomSrtm']
                paris_tennis.postal_code = tennis['properties']['general']['_codePostal']
                paris_tennis.address = tennis['properties']['general']['_adresse']
                paris_tennis.town = tennis['properties']['general']['_ville']
                paris_tennis.phone = tennis['properties']['general']['_telephone']
                for court in tennis['properties']['courts']:
                    tennis_court = TennisCourt()
                    tennis_court.set_indoor(court_dict=court)
                    tennis_court.set_lighting(court_dict=court)
                    tennis_court.set_court_number(court_dict=court)
                    tennis_court.set_coating(court_dict=court)
                    paris_tennis.tennis_courts.append(tennis_court)
                results.append(paris_tennis)

        print(results)

    def get_dispo(self):
        self.set_cookie()
        url = """https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&action=disponibilite"""
        payload = """hourRange=8-22&when=21%2F09%2F2023&selWhereTennisName=Elisabeth&selInOut%5B%5D=V&selInOut%5B%5D=F&selCoating%5B%5D=96&selCoating%5B%5D=2095&selCoating%5B%5D=94&selCoating%5B%5D=1324&selCoating%5B%5D=2016&selCoating%5B%5D=92"""
        response = requests.post(url=url,
                                 data=payload,
                                 cookies=self.cookies,
                                 headers=self.headers,
                                 allow_redirects=True)
        print(response.status_code)
        print(response.content)
        print(self.cookies)


if __name__ == '__main__':
    check_courts = CheckAvailableCourts(alarm_date_time=datetime(2023, 9, 21),
                                        court_names=['atlantique'])
    check_courts.get_dispo()
    check_courts.get_available(trade_date=datetime(2023, 9, 21))
