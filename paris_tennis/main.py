from paris_tennis.tennis_scanner.scan_courts import ParisTennis
import asyncio

if __name__ == '__main__':
    paris_tennis = ParisTennis(headless=True)

    asyncio.get_event_loop().run_until_complete(paris_tennis.check_all_availabilities())
