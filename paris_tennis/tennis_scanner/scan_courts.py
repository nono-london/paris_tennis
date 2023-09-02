import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Union, Optional

from bs4 import BeautifulSoup as bs
from playwright.async_api import async_playwright, Page, Browser, Locator, TimeoutError

from paris_tennis.app_config import get_tennis_names


@dataclass(repr=True)
class CourtType:
    tennis_indoor: bool = False
    tennis_hour: int = -1
    court_number: int = -1

    @staticmethod
    def is_indoor(tennis_desc: str) -> bool:
        print(tennis_desc)
        return "Découvert" not in tennis_desc

    @staticmethod
    def get_tennis_number(tennis_desc: str) -> int:
        court_number = -1
        try:
            court_number = tennis_desc.split("Court N°")[-1].split(" ")[0].strip()
            court_number = int(court_number)
        except ValueError as ex:
            print(f'Issue while getting tennis court number from:"{tennis_desc}"\n'
                  f'Error: {ex}')
        return court_number


@dataclass(repr=True)
class TennisCourtSummary:
    tennis_date: datetime = datetime(1900, 1, 1)
    available_courts: int = 0
    available_hours_courts: List[CourtType] = field(default_factory=lambda: list())


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
            self.browser = await self.APW.webkit.launch(headless=self.headless)
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

    async def get_available_dates(self) -> Union[None, List[TennisCourtSummary]]:
        page_source = await self.page.content()
        web_soup = bs(page_source, 'lxml')

        court_dates = web_soup.find_all(name='div', attrs={'class': 'date-item'})
        if len(court_dates) != 7:
            print(f"Error while getting the number of dates available")
            return None
        #
        for court_date in court_dates:
            tennis_court_summary = TennisCourtSummary()
            # get court date
            court_date_el = court_date.find(name='div', attrs={'class': 'date'})
            if court_date_el:
                court_date_str = court_date_el.get('dateiso')
                if court_date:
                    tennis_court_summary.tennis_date = datetime.strptime(court_date_str, '%d/%m/%Y')

            # get number of courts available, if None, means no courts are available
            court_number_el = court_date.find(name='div', attrs={'class': 'digits'})
            if court_number_el:
                court_number = court_number_el.get_text()
                tennis_court_summary.available_courts = int(court_number)
            self.tennis_summaries.append(tennis_court_summary)

        return self.tennis_summaries

    async def loop_through_week(self):
        await self.page.wait_for_timeout(5000)
        week_days_xpath: str = "xpath=// div[contains(@class,'date-item')]"
        # find date elements
        week_date_els: List[Locator] = await self.page.locator(week_days_xpath).all()
        print(f'Size of date elements: {len(week_date_els)}')
        for index, week_date_el in enumerate(week_date_els, start=0):
            print(f'Day: {index + 1}')
            try:
                # print(await week_date_els[index].text_content())
                await week_date_els[index].click(delay=100)
                await self.page.wait_for_timeout(5000)
                await self.get_available_hours(self.tennis_summaries[index])

            except TimeoutError as ex:
                print(ex)
                print(f"Error while clicking on element")
                continue

            # refresh the list of elements as class names changes with JS selection
            week_date_els: List[Locator] = await self.page.locator(week_days_xpath).all()

    async def get_available_hours(self, tennis_court: TennisCourtSummary) -> List:
        web_soup = bs(await self.page.content(), 'lxml')
        search_block_el = web_soup.find("div", attrs={'class': 'search-result-block'})
        hour_els: List = search_block_el.find_all("div", attrs={'class': "panel panel-default"})
        print(f'Found {len(hour_els)} hours available')
        for hour_el in hour_els:
            # find hour
            hour_str = hour_el.find("div", attrs={'class': 'panel-heading'})
            try:
                hour_int = hour_str.text.replace("h", "").strip()
            except ValueError as ex:
                print(f'Error while extracting hour: {ex}')
                continue
            # find courts' details
            court_els = hour_el.find_all("div", attrs={'class': 'row tennis-court'})
            for court_el in court_els:
                tennis_type = CourtType()
                tennis_type.tennis_hour = int(hour_int)
                # court number
                court_number = court_el.find("span", attrs={"class": "court"})
                try:
                    tennis_type.court_number = tennis_type.get_tennis_number(tennis_desc=court_number.text.strip())
                except ValueError as ex:
                    print(f"Couldn't find court details, error: {ex}")
                # couvert /decouvert
                court_desc = court_el.find("small", attrs={"class": "price-description"})
                try:
                    tennis_type.tennis_indoor = tennis_type.is_indoor(tennis_desc=court_desc.text.strip())
                except ValueError as ex:
                    print(f"Couldn't find court details, error: {ex}")
                tennis_court.available_hours_courts.append(tennis_type)

    async def check_all_availabilities(self):
        await self.select_a_court()
        await self.page.wait_for_timeout(5000)

        await self.get_available_dates()
        # print(self.tennis_summaries)
        await self.loop_through_week()
        await self.page.wait_for_timeout(10000)
        print(self.tennis_summaries)


if __name__ == '__main__':
    paris_tennis = ParisTennis()

    asyncio.get_event_loop().run_until_complete(paris_tennis.check_all_availabilities())
