from typing import Union, List, Dict


class TennisCourt:
    def __init__(self):
        self.indoor: bool = False
        self.lighting: bool = False
        self.court_number: int = -1
        self.coating: str = ''

    def set_indoor(self, court_dict: Dict):
        self.indoor = court_dict.get('_airCvt') == "V"

    def set_lighting(self, court_dict: Dict):
        self.lighting = court_dict.get('_airEcl') == "V"

    def set_court_number(self, court_dict: Dict):
        self.court_number = court_dict.get('_formattedAirNum')

    def set_coating(self, court_dict: Dict):
        self.coating = court_dict.get('_coating').get('_revLib')


class ParisTennis:
    def __init__(self):
        self.name: str = ''
        self.postal_code: str = ''
        self.address: str = ''
        self.town: str = ''
        self.phone: str = ''
        self.tennis_courts: List[TennisCourt] = []

    def __repr__(self):
        return f'{self.name}, {len(self.tennis_courts)} courts'


if __name__ == '__main__':
    pass
