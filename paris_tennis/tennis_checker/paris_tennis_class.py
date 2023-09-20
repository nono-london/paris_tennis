from typing import Union


class ParisTennis:
    def __init__(self):
        self.court_number: int = -1

    def set_court_number(self, court_number: str) -> Union[int, None]:
        try:
            court_number = court_number.split(" ")[-1]
            return int(court_number)
        except Exception as ex:
            print(f'Error with Court number')
            print(ex)
            return None

    def set_indoor(self, indoor_data:str):
        return indoor_data=='V'


if __name__ == '__main__':
    pass
