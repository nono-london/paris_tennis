import asyncio
from datetime import datetime
from typing import List, Union, Optional

from playwright.async_api import async_playwright, Page, Browser

from paris_tennis.app_config import get_tennis_names


class ParisTennis:
    def __init__(self, headless: bool = False):
        self.headless: bool = headless
        self.main_url: str = 'https://tennis.paris.fr/tennis/jsp/site/Portal.jsp?page=recherche&view=recherche_creneau#!'
        self.tennis_names: List = get_tennis_names()
        self.APW: Union[async_playwright, None] = None
        self.browser: Union[Browser, None] = None
        self.page: Union[Page, None] = None
        self.day_checked: datetime = datetime(1900, 1, 1)

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
        await self.page.wait_for_timeout(50000)


if __name__ == '__main__':
    paris_tennis = ParisTennis()

    asyncio.get_event_loop().run_until_complete(paris_tennis.select_a_court())
