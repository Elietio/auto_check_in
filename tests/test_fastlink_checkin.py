import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import requests

# Add the parent directory to the sys.path to allow imports from the 'fastlink' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastlink import fastlink_checkin

class TestFastlinkCheckin(unittest.TestCase):

    @patch('fastlink.fastlink_checkin.requests.Session')
    def test_main_success(self, mock_session):
        """Test successful login and check-in."""
        # Mock the session object
        mock_sess_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_sess_instance

        # Mock the login response
        mock_login_response = MagicMock()
        mock_login_response.json.return_value = {'ret': 1, 'msg': 'Login successful'}
        mock_login_response.raise_for_status.return_value = None

        # Mock the check-in response
        mock_checkin_response = MagicMock()
        mock_checkin_response.json.return_value = {'ret': 1, 'msg': 'Check-in successful'}
        mock_checkin_response.raise_for_status.return_value = None

        # Configure the session's post method to return the mocked responses
        mock_sess_instance.post.side_effect = [mock_login_response, mock_checkin_response]

        # Run the main function
        fastlink_checkin.main()

        # Assert that the post method was called twice
        self.assertEqual(mock_sess_instance.post.call_count, 2)

    @patch('fastlink.fastlink_checkin.requests.Session')
    def test_main_login_failure(self, mock_session):
        """Test a failed login attempt."""
        # Mock the session object
        mock_sess_instance = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_sess_instance

        # Mock a failed login response
        mock_login_response = MagicMock()
        mock_login_response.json.return_value = {'ret': 0, 'msg': 'Invalid credentials'}
        mock_login_response.raise_for_status.side_effect = requests.exceptions.HTTPError

        # Configure the session's post method to return the mocked response
        mock_sess_instance.post.return_value = mock_login_response

        # Run the main function
        fastlink_checkin.main()

        # Assert that the post method was called only once
        self.assertEqual(mock_sess_instance.post.call_count, 1)

if __name__ == '__main__':
    unittest.main()