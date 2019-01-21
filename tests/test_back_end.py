"""Back end tests for Dream Team."""

import unittest

from flask import abort, url_for
from flask_testing import TestCase

from app import create_app, db
from app.models import Department, Employee, Role


class TestBase(TestCase):
    """Base test class."""

    def create_app(self):
        """Create app with test configuration."""
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='mysql+pymysql://'
                                    'dt_admin:dt2019@localhost/'
                                    'dreamteam_test'
        )
        return app

    def setUp(self):
        """Set up the testing environment."""
        db.session.commit()
        db.drop_all()
        db.create_all()

        admin = Employee(
            username='admin',
            password='admin2019',
            is_admin=True
        )

        employee = Employee(
            username='test_user',
            password='test2019'
        )

        db.session.add(admin)
        db.session.add(employee)
        db.session.commit()

    def tearDown(self):
        """Tear down the test environment."""
        db.session.remove()
        db.drop_all()


class TestModels(TestBase):
    """Test the app's models."""

    def test_employee_model(self):
        """Test number of records in Employee table."""
        self.assertEqual(Employee.query.count(), 2)

    def test_department_model(self):
        """Test number of records in Department table."""
        department = Department(
            name='IT',
            description='The IT Department'
        )

        db.session.add(department)
        db.session.commit()

        self.assertEqual(Department.query.count(), 1)

    def test_role_model(self):
        """Test number of records in Role table."""
        role = Role(
            name='CEO',
            description='Run the whole company'
        )

        db.session.add(role)
        db.session.commit()

        self.assertEqual(Role.query.count(), 1)


class TestViews(TestBase):
    """Test the app's views."""

    def test_homepage_view(self):
        """Test that the homepage is accessible without login."""
        response = self.client.get(url_for('home.homepage'))
        self.assertEqual(response.status_code, 200)

    def test_login_view(self):
        """Test that login page is accessible without login."""
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """Test that logout link is inaccessible without login
           and redirects to login page then to logout."""
        target_url = url_for('auth.logout')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_dashboard_view(self):
        """Test that dashboard is inaccessible without login
           and redirects to login page then to dashboard."""
        target_url = url_for('home.dashboard')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_admin_dashboard_view(self):
        """Test that dashboard is inaccessible without login
           and redirects to loin page then to dashboard."""
        target_url = url_for('home.admin_dashboard')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_departments_view(self):
        """Test that departments page is inaccessible without login
           and redirects to login page then to department."""
        target_url = url_for('admin.list_departments')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_roles_view(self):
        """Test that roles page is inaccessible without login
           and redirects to login page then to roles page."""
        target_url = url_for('admin.list_roles')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)

    def test_employees_view(self):
        """Test that employees page is inaccessible without login
           and redirects to login page then to employees page."""
        target_url = url_for('admin.list_employees')
        redirect_url = url_for('auth.login', next=target_url)
        response = self.client.get(target_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, redirect_url)


class TestErrorPages(TestBase):
    """Test the error pages."""

    def test_403_forbidden(self):
        """Test the 403: Forbidden view."""
        @self.app.route('/403')
        def forbidden_error():
            abort(403)

        response = self.client.get('/403')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(b'403 Error' in response.data)

    def test_404_not_found(self):
        """Test 404: Not Found view."""
        response = self.client.get('/nothinghere')
        self.assertEqual(response.status_code, 404)
        self.assertTrue(b'404 Error' in response.data)

    def test_500_internal_server_error(self):
        """Test 500: Internal Server Error view."""
        @self.app.route('/500')
        def internal_server_error():
            abort(500)

        response = self.client.get('/500')
        self.assertEqual(response.status_code, 500)
        self.assertTrue(b'500 Error' in response.data)


if __name__ == '__main__':
    unittest.main()
