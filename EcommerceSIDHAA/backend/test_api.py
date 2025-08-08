import unittest
import json
from app import app, db
from app.models import User, Product

class ApiTestCase(unittest.TestCase):
    def setUp(self):
        """Set up a test client and a test database."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down the database."""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_delete_product_unauthorized(self):
        """Test that deleting a product without auth fails."""
        # First, create a product to delete
        with app.app_context():
            p = Product(name='Test Product', description='A test product', price=10.0)
            db.session.add(p)
            db.session.commit()
            product_id = p.id

        # Attempt to delete the product without the x-user-id header
        response = self.client.delete(f'/products/{product_id}')

        # Check that the response is 401 Unauthorized
        self.assertEqual(response.status_code, 401)
        self.assertIn('User ID is missing!', response.get_data(as_text=True))

    def test_create_product_unauthorized(self):
        """Test that creating a product without auth fails."""
        response = self.client.post('/products',
                                    data=json.dumps({'name': 'New Product', 'price': 20.0}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('User ID is missing!', response.get_data(as_text=True))

    def test_update_product_unauthorized(self):
        """Test that updating a product without auth fails."""
        # First, create a product to update
        with app.app_context():
            p = Product(name='Test Product', description='A test product', price=10.0)
            db.session.add(p)
            db.session.commit()
            product_id = p.id

        response = self.client.put(f'/products/{product_id}',
                                   data=json.dumps({'name': 'Updated Name'}),
                                   content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('User ID is missing!', response.get_data(as_text=True))

    def test_update_profile(self):
        """Test updating a user's profile."""
        with app.app_context():
            u = User(username='testuser', email='test@test.com')
            u.set_password('password')
            db.session.add(u)
            db.session.commit()
            user_id = u.id

        headers = {'x-user-id': user_id}
        update_data = {'username': 'newname', 'email': 'new@test.com'}
        response = self.client.put('/profile', headers=headers, data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        with app.app_context():
            updated_user = User.query.get(user_id)
            self.assertEqual(updated_user.username, 'newname')
            self.assertEqual(updated_user.email, 'new@test.com')

    def test_change_password(self):
        """Test changing a user's password."""
        with app.app_context():
            u = User(username='testuser', email='test@test.com')
            u.set_password('oldpassword')
            db.session.add(u)
            db.session.commit()
            user_id = u.id

        headers = {'x-user-id': user_id}
        password_data = {'old_password': 'oldpassword', 'new_password': 'newpassword'}
        response = self.client.post('/profile/change-password', headers=headers, data=json.dumps(password_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Verify new password works
        with app.app_context():
            user = User.query.get(user_id)
            self.assertTrue(user.check_password('newpassword'))
            self.assertFalse(user.check_password('oldpassword'))

    def test_change_password_wrong_old(self):
        """Test changing password with wrong old password."""
        with app.app_context():
            u = User(username='testuser', email='test@test.com')
            u.set_password('oldpassword')
            db.session.add(u)
            db.session.commit()
            user_id = u.id

        headers = {'x-user-id': user_id}
        password_data = {'old_password': 'wrongpassword', 'new_password': 'newpassword'}
        response = self.client.post('/profile/change-password', headers=headers, data=json.dumps(password_data), content_type='application/json')
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
