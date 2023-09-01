import asyncio
from datetime import datetime
from typing import List, Union, Optional
from bs4 import BeautifulSoup as bs
from numpy.f2py.symbolic import COUNTER
from playwright.async_api import async_playwright, Page, Browser

from paris_tennis.app_config import get_tennis_names
from dataclasses import dataclass


class ParisTennis:
    def __init__(self, headless: bool = False):
        self.headless: bool = headless
        self.main_url: str = 'https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&view=recherche_creneau#!'
        self.tennis_names: List = get_tennis_names()
        self.APW: Union[async_playwright, None] = None
        self.browser: Union[Browser, None] = None
        self.page: Union[Page, None] = None
        self.day_checked: datetime = datetime(1900, 1, 1)
        self.tennis_summaries: List[TennisCourtSummary] = list()

    async def start_browser(self):
        if not self.page:
            self.APW = await async_playwright().start()
            self.browser = await self.APW.firefox.launch(headless=self.headless)
            self.page = await self.browser.new_page()

    async def select_a_court(self, court_name: Optional[str] = None):
        if not court_name:
            court_name = self.tennis_names[0]
        print(f'Launching search for court: {court_name}')

        # check/start browser
        await self.start_browser()
        await self.page.goto(self.main_url)

        # select court location
        where_token = self.page.locator('xpath=//*[@id="whereToken"]/ li / input')
        await where_token.click()
        await self.page.keyboard.type(court_name, delay=100)
        await self.page.keyboard.press(key='ArrowDown', delay=100)
        await self.page.keyboard.press(key='Enter', delay=100)

        submit_element = self.page.locator('xpath=//button[@id="rechercher"]')
        await submit_element.click(delay=100)

    async def get_available_dates(self):
        page_source = await self.page.content()
        web_soup = bs(page_source, 'lxml')

        court_dates = web_soup.find_all(name='div', attrs={'class': 'date-item'})
        print(len(court_dates))
        #
        for court_date in court_dates:
            tennis_court_summary = TennisCourtSummary()
            # get court date
            court_date_el = court_date.find(name='div', attrs={'class': 'date'})
            if court_date_el:
                court_date_str = court_date_el.get('dateiso')
                if court_date:
                    tennis_court_summary.tennis_date = datetime.strptime(court_date_str, '%d/%m/%Y')
                print(tennis_court_summary.tennis_date)
            # get number of courts available
            court_number_el = court_date.find(name='div', attrs={'class': 'digits'})
            if court_number_el:
                court_number = court_number_el.get_text()
                tennis_court_summary.available_courts = int(court_number)
            self.tennis_summaries.append(tennis_court_summary)

    async def check_all_availabilities(self):
        await self.select_a_court()
        await self.page.wait_for_timeout(5000)

        await self.get_available_dates()
        print(self.tennis_summaries)

        await self.page.wait_for_timeout(50000)


@dataclass(repr=True)
class TennisCourtSummary:
    tennis_date: datetime = datetime(1900, 1, 1)
    available_courts: int = 0


if __name__ == '__main__':
    paris_tennis = ParisTennis()

    asyncio.get_event_loop().run_until_complete(paris_tennis.check_all_availabilities())
