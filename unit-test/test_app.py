from unicodedata import name
from unittest.mock import patch
from app import calcul_factorial, get_user

from unittest import TestCase, main, result


class AppTest(TestCase):
    def test_calcul_factorial_positive(self):
        # Given
        number = 3
        expected_result = 6

        # When
        result = calcul_factorial(number)

        # Then
        assert expected_result == result

    def test_calcul_factorial_zero(self):
        # Given
        number = 0
        expected_result = 1

        # When
        result = calcul_factorial(number)

        # Then
        self.assertEqual(expected_result, result)

    def test_calcul_factorial_negative(self):
        # Given
        number = -3

        # Then
        self.assertRaises(ValueError, calcul_factorial, number)


class TestGetUser(TestCase):

    @patch("app.sqlite3")
    def test_get_user(self, mocked_object):
        # Given
        mocked_object.connect().execute().fetchone.return_value = (
            1, "Souha", "Souha Ben Hassine")
        expected_user = {
            "id": 1,
            "username": "Souha",
            "fullname": "Souha Ben Hassine",
        }

        # When
        result = get_user(1)

        # Then
        self.assertDictEqual(result, expected_user)


if __name__ == "__main__":
    main()
