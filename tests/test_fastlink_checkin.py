import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import requests
import json

# Add the parent directory to the sys.path to allow imports from the 'fastlink' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastlink import fastlink_checkin

class TestFastlinkCheckin(unittest.TestCase):

    @patch('fastlink.fastlink_checkin.requests.Session')
    @patch('fastlink.fastlink_checkin.send_notification')
    def test_main_success(self, mock_send_notification, mock_session):
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

        # Mock the user info response
        mock_user_response = MagicMock()
        # 提供一个模拟的HTML响应，包含所有需要提取的信息
        mock_user_response.text = '''
        <div class="user-info">
            <p>"Unused_Traffic", "10.00 GB"</p>
            <p>"Traffic_RestDay", "2025-08-10"</p>
            <p>今日已用: 1.25 GB</p>
            <p>官网网址: <a href="https://example.com">https://example.com</a></p>
            <p>备用网址: <a href="https://backup.example.com">https://backup.example.com</a></p>
            <p>国内加速: <a href="https://cn.example.com">https://cn.example.com</a></p>
            <p>优惠码: DISCOUNT123</p>
        </div>
        '''
        mock_user_response.raise_for_status.return_value = None
        mock_user_response.encoding = None

        # Configure the session's methods to return the mocked responses
        mock_sess_instance.post.side_effect = [mock_login_response, mock_checkin_response]
        mock_sess_instance.get.return_value = mock_user_response

        # Run the main function
        fastlink_checkin.main()

        # Assert that the post method was called twice (login and check-in)
        self.assertEqual(mock_sess_instance.post.call_count, 2)
        
        # Assert that the get method was called once (user info)
        self.assertEqual(mock_sess_instance.get.call_count, 1)
        
        # Assert that send_notification was called with the correct arguments
        mock_send_notification.assert_called_once()
        args, kwargs = mock_send_notification.call_args
        self.assertEqual(args[0], "fastlink 签到")
        self.assertIn("- 签到信息: Check-in successful", args[1])
        self.assertIn("- 剩余流量: 10.00 GB", args[1])
        self.assertEqual(kwargs.get('tags'), "签到")

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

    @patch('fastlink.fastlink_checkin.requests.post')
    def test_send_notification_serverchan(self, mock_post):
        """Test ServerChan notification."""
        # 保存原始值
        original_sendkey = fastlink_checkin.SERVERCHAN_SENDKEY
        original_uid = fastlink_checkin.SERVERCHAN_UID
        
        # 设置测试值
        fastlink_checkin.SERVERCHAN_SENDKEY = "test_key"
        fastlink_checkin.SERVERCHAN_UID = "test_uid"
        
        # 模拟成功响应
        mock_response = MagicMock()
        mock_response.json.return_value = {"code": 0}
        mock_post.return_value = mock_response
        
        # 调用函数
        fastlink_checkin.send_notification_serverchan("Test Title", "Test Message", "test_tag")
        
        # 验证请求
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test_uid.push.ft07.com/send/test_key.send")
        self.assertEqual(kwargs['data']['title'], "Test Title")
        self.assertEqual(kwargs['data']['desp'], "Test Message")
        self.assertEqual(kwargs['data']['tags'], "test_tag")
        
        # 恢复原始值
        fastlink_checkin.SERVERCHAN_SENDKEY = original_sendkey
        fastlink_checkin.SERVERCHAN_UID = original_uid

    @patch('fastlink.fastlink_checkin.requests.post')
    def test_send_notification_fcm(self, mock_post):
        """Test FCM notification."""
        # 保存原始值
        original_token = fastlink_checkin.FCM_TOKEN
        original_endpoint = fastlink_checkin.FCM_ENDPOINT
        
        # 设置测试值
        fastlink_checkin.FCM_TOKEN = "test_token"
        fastlink_checkin.FCM_ENDPOINT = "https://test-endpoint.com"
        
        # 模拟成功响应
        mock_response = MagicMock()
        mock_post.return_value = mock_response
        
        # 调用函数
        fastlink_checkin.send_notification_fcm("Test Title", "Test Message")
        
        # 验证请求
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://test-endpoint.com")
        self.assertEqual(kwargs['headers']['Content-Type'], "application/json")
        
        # 验证 JSON 数据
        payload = json.loads(kwargs['data'])
        self.assertEqual(payload['data']['to'], "test_token")
        self.assertEqual(payload['data']['data']['text']['title'], "Test Title")
        self.assertEqual(payload['data']['data']['text']['message'], "Test Message")
        
        # 恢复原始值
        fastlink_checkin.FCM_TOKEN = original_token
        fastlink_checkin.FCM_ENDPOINT = original_endpoint

    @patch('fastlink.fastlink_checkin.send_notification_serverchan')
    @patch('fastlink.fastlink_checkin.send_notification_fcm')
    def test_send_notification_method_selection(self, mock_fcm, mock_serverchan):
        """Test notification method selection."""
        # 保存原始值
        original_method = fastlink_checkin.PUSH_METHOD
        
        # 测试 ServerChan
        fastlink_checkin.PUSH_METHOD = "serverchan"
        fastlink_checkin.send_notification("Test Title", "Test Message", "test_tag")
        mock_serverchan.assert_called_once_with("Test Title", "Test Message", "test_tag")
        mock_fcm.assert_not_called()
        
        # 重置 mock
        mock_serverchan.reset_mock()
        mock_fcm.reset_mock()
        
        # 测试 FCM
        fastlink_checkin.PUSH_METHOD = "fcm"
        fastlink_checkin.send_notification("Test Title", "Test Message", "test_tag")
        mock_fcm.assert_called_once_with("Test Title", "Test Message")
        mock_serverchan.assert_not_called()
        
        # 恢复原始值
        fastlink_checkin.PUSH_METHOD = original_method

if __name__ == '__main__':
    unittest.main()