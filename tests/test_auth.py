import unittest
from app import create_app, db
from app.models.user import User

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(Config)
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True
        
    def test_register(self):
        """Test user registration"""
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'first_name': 'Test',
            'last_name': 'User'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
    def test_login(self):
        """Test user login"""
        # First register
        self.client.post('/auth/register', data={
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password