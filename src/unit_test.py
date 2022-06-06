import importlib
import unittest
import pandas as pd
from unittest.mock import patch, Mock
from service.concert_service import ConcertService

from repository.musician_repository import MusicianRepository
from model.musician import Musician
from service.musician_service import MusicianService

class ConcertServiceTest(unittest.TestCase):
#test should organize concert with default values
    def test_organize_concert_default(self):
        # given
        concert_service = ConcertService()
        # when
        concert_details = concert_service.organize_concert()
        # then
        self.assertIsNotNone(concert_details)
        self.assertEqual(concert_details['band'], 'Nirvana')
        self.assertEqual(concert_details['ticket_price'], 10)
    @patch("service.ticket_service.TicketService.define_ticket_price")
    @patch("service.organization_service.OrganizationService.choose_band")
    #test should organize concert with mocked values
    def test_organize_concert_mocked_values(self,mock_choose_band,mock_define_ticket_price):
        # given
        concert_service = ConcertService()
        mock_choose_band.return_value = "Guns and Roses"
        mock_define_ticket_price.return_value = 200
        # when
        concert_details = concert_service.organize_concert()
        # then
        self.assertIsNotNone(concert_details)
        self.assertEqual(concert_details['band'], 'Guns and Roses')
        self.assertEqual(concert_details['ticket_price'], 200)

class MusicianRepositoryTest(unittest.TestCase):
    #test should get musician 
    def test_get_musician(self):
        # given
        client = Mock()
        client.retrieve_musician.return_value = pd.DataFrame({'name': ['ed'],'surname': ['sherran'],'age': [31],'instrument': ['guitar']})
        musician_repository = MusicianRepository(postgres_client=client)
        # when
        musician = musician_repository.get_musician('ed')
        # then
        self.assertIsNotNone(musician)
        self.assertEqual(musician.name, 'ed')
        self.assertEqual(musician.surname, 'sherran')
        self.assertEqual(musician.age, 31)
        self.assertEqual(musician.instrument, 'guitar')

class MusicianServiceTest(unittest.TestCase):

    def test_get_musician_by_name(self):
        # given
        musician_repository = Mock()
        musician_repository.get_musician.return_value = Musician(name='ed',
                                                                 surname='sherran',
                                                                 age=31,
                                                                 instrument='guitar')
        external_musicians_client = Mock()

        musician_service = MusicianService(musician_repository=musician_repository,
                                           external_musician_client=external_musicians_client)

        # when
        musician = musician_service.get_musician_by_name('ed')

        # then
        self.assertIsNotNone(musician)
        self.assertEqual(musician.name, 'ed')
        self.assertEqual(musician.surname, 'sherran')
        self.assertEqual(musician.age, 31)
        self.assertEqual(musician.instrument, 'guitar')

    def test_validate_name(self):
        # given
        musician_repository = Mock()
        external_musicians_client = Mock()
        musician_service = MusicianService(musician_repository=musician_repository, external_musician_client=external_musicians_client)
        # when
        with self.assertRaises(Exception) as context:
            musician_service.get_musician_by_name('ed9')
        # then
        self.assertTrue('Name is invalid.' in str(context.exception))
