"""Front-end/functional tests for Dream Team app."""

import time
import unittest

import requests

from flask import url_for
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from app import create_app, db
from app.models import Employee, Role, Department


test_admin_username = 'admin'
test_admin_email = 'admin@email.com'
test_admin_password = 'admin2019'

test_employee1_first_name = 'Test'
test_employee1_last_name = 'Employee'
test_employee1_username = 'employee1'
test_employee1_email = 'employee1@email.com'
test_employee1_password = '1test2019'

test_employee2_first_name = 'Test'
test_employee2_last_name = 'Employee'
test_employee2_username = 'employee2'
test_employee2_email = 'employee2@email.com'
test_employee2_password = '2test2019'

test_department1_name = 'Human Resources'
test_department1_description = 'Find and keep the best talent'

test_department2_name = 'Information Technology'
test_department2_description = 'Manage all tech systems and processes'

test_role1_name = 'Head of Department'
test_role1_description = 'Lead the entire department'

test_role2_name = 'Intern'
test_role2_description = '3-month learning position'


class TestBase(LiveServerTestCase):
    """Base test case."""

    def create_app(self):
        """Create the app for testing."""
        config_name = 'testing'
        app = create_app(config_name)
        app.config.update(
            SQLALCHEMY_DATABASE_URI='mysql+pymysql://'
                                    'dt_admin:dt2019@localhost/'
                                    'dreamteam_test',
            LIVESERVER_PORT=8943
        )
        return app

    def setUp(self):
        """Setup the test driver and create test users."""
        self.driver = webdriver.Chrome()
        self.driver.get(self.get_server_url())

        db.session.commit()
        db.drop_all()
        db.create_all()

        self.admin = Employee(username=test_admin_username,
                              email=test_admin_email,
                              password=test_admin_password,
                              is_admin=True)

        self.employee = Employee(username=test_employee1_username,
                                 first_name=test_employee1_first_name,
                                 last_name=test_employee1_last_name,
                                 email=test_employee1_email,
                                 password=test_employee1_password)

        self.department = Department(name=test_department1_name,
                                     description=test_department1_description)

        self.role = Role(name=test_role1_name,
                         description=test_role1_description)

        db.session.add(self.admin)
        db.session.add(self.employee)
        db.session.add(self.department)
        db.session.add(self.role)
        db.session.commit()

    def tearDown(self):
        self.driver.quit()

    def test_server_is_up_and_running(self):
        response = requests.get(self.get_server_url())
        self.assertEqual(response.status_code, 200)


class TestRegistration(TestBase):
    """Test a user registration."""

    def test_registration(self):
        """Test that a user can create an account using the registration form
           if all fields are filled out correctly, and that they will be
           redirected to the login page."""
        self.driver.find_element_by_id('register_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys(test_employee2_email)
        self.driver.find_element_by_id('username').send_keys(
            test_employee2_username)
        self.driver.find_element_by_id('first_name').send_keys(
            test_employee2_first_name)
        self.driver.find_element_by_id('last_name').send_keys(
            test_employee2_last_name)
        self.driver.find_element_by_id('password').send_keys(
            test_employee2_password)
        self.driver.find_element_by_id('confirm_password').send_keys(
            test_employee2_password)
        self.driver.find_element_by_id('submit').click()
        time.sleep(1)

        assert url_for('auth.login') in self.driver.current_url

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully registered' in success_message

        self.assertEqual(Employee.query.count(), 3)

    def test_registration_invalid_email(self):
        """Test that a user cannot register using an invalid email format
           and that an appropriate error message will be displayed."""

        self.driver.find_element_by_id('register_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys('invalid_email')
        self.driver.find_element_by_id('username').send_keys(
            test_employee2_username)
        self.driver.find_element_by_id('first_name').send_keys(
            test_employee2_first_name)
        self.driver.find_element_by_id('last_name').send_keys(
            test_employee2_last_name)
        self.driver.find_element_by_id('password').send_keys(
            test_employee2_password)
        self.driver.find_element_by_id('confirm_password').send_keys(
            test_employee2_password)
        self.driver.find_element_by_id('submit').click()
        time.sleep(5)

        error_message = self.driver.find_element_by_class_name(
            'help-block').text
        assert 'Invalid email address' in error_message

    def test_registration_confirm_password(self):
        """Test that an appropriate error message is displayed when the password
           and confirm_password fields do not match."""
        self.driver.find_element_by_id('register_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys(test_employee2_email)
        self.driver.find_element_by_id('username').send_keys(
            test_employee2_username)
        self.driver.find_element_by_id('first_name').send_keys(
            test_employee2_first_name)
        self.driver.find_element_by_id('last_name').send_keys(
            test_employee2_last_name)
        self.driver.find_element_by_id('password').send_keys(
            test_employee2_password)
        self.driver.find_element_by_id('confirm_password').send_keys(
            "password-won't-match")
        self.driver.find_element_by_id('submit').click()
        time.sleep(5)

        error_message = self.driver.find_element_by_class_name(
            'help-block').text
        assert 'Field must be equal to confirm_password' in error_message


class CreateObjects(object):

    def login_admin_user(self):
        """Login as the test employee."""
        login_link = self.get_server_url() + url_for('auth.login')
        self.driver.get(login_link)
        self.driver.find_element_by_id('email').send_keys(test_admin_email)
        self.driver.find_element_by_id('password').send_keys(
            test_admin_password)
        self.driver.find_element_by_id('submit').click()

    def login_test_user(self):
        """Login as the test employee."""
        login_link = self.get_server_url() + url_for('auth.login')
        self.driver.get(login_link)
        self.driver.find_element_by_id('email').send_keys(test_employee1_email)
        self.driver.find_element_by_id('password').send_keys(
            test_employee1_password)
        self.driver.find_element_by_id('submit').click()


class TestLogin(TestBase):
    """Test the ability to login."""

    def test_login(self):
        """Test that a user can login and that they will be redirected to
           the homepage."""
        self.driver.find_element_by_id('login_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys(test_employee1_email)
        self.driver.find_element_by_id('password').send_keys(
            test_employee1_password)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        assert url_for('home.dashboard') in self.driver.current_url

        username_greeting = self.driver.find_element_by_id(
            'username_greeting').text
        assert 'Hi, employee1!' in username_greeting

    def test_admin_login(self):
        """Test that an admin user can login and that they will be redirected to
           the admin homepage."""
        self.driver.find_element_by_id('login_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys(test_admin_email)
        self.driver.find_element_by_id('password').send_keys(
            test_admin_password)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        assert url_for('home.admin_dashboard') in self.driver.current_url

        username_greeting = self.driver.find_element_by_id(
            'username_greeting').text
        assert 'Hi, admin!' in username_greeting

    def test_login_invalid_email_format(self):
        """Test that a user cannot login using an invalid email format
           and taht an appropriate error message will be displayed."""
        self.driver.find_element_by_id('login_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys('invalid')
        self.driver.find_element_by_id('password').send_keys(
            test_employee1_password)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        error_message = self.driver.find_element_by_class_name(
            'help-block').text
        assert 'Invalid email address' in error_message

    def test_login_wrong_email(self):
        """Test that a user cannot ogin using the wrong email address
           and that an appropriate error message will be displayed."""
        self.driver.find_element_by_id('login_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys(test_employee2_email)
        self.driver.find_element_by_id('password').send_keys(
            test_employee1_password)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        error_message = self.driver.find_element_by_class_name('alert').text
        assert 'Invalid email or password' in error_message

    def test_login_wrong_password(self):
        """Test that a user cannot login using the wrong password
           and that an appropriate error message will be displayed."""
        self.driver.find_element_by_id('login_link').click()
        time.sleep(1)

        self.driver.find_element_by_id('email').send_keys(test_employee1_email)
        self.driver.find_element_by_id('password').send_keys('invalid')
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        error_message = self.driver.find_element_by_class_name('alert').text
        assert 'Invalid email or password' in error_message


def TestDepartments(CreateObjects, TestBase):

    def test_add_department(self):
        """Test that an admin user can add a department."""
        self.login_admin_user()

        self.driver.find_element_by_id('departments_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('btn').click()
        time.sleep(1)

        self.driver.find_element_by_id('name').send_keys(test_department2_name)
        self.driver.find_element_by_id('description').send_keys(
            test_department2_description)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully added a new department' in success_message

        self.assertEqual(Department.query.count(), 2)

    def test_add_existing_department(self):
        """Test that an admin user cannot add a deparmtment with a name that
           already exists."""
        self.login_admin_user()

        self.driver.find_element_by_id('departments_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('btn').click()
        time.sleep(1)

        self.driver.find_element_by_id('name').send_keys(test_department1_name)
        self.driver.find_element_by_id('description').send_keys(
            test_department1_description)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        error_message = self.driver.find_element_by_class_name('alert').text
        assert 'Error: department name already exists' in error_message

    def test_edit_department(self):
        """Test that an admin user can edit a department."""
        self.login_admin_user()

        self.driver.find_element_by_id('departments_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('fa-pencil').click()
        time.sleep(1)

        self.driver.find_element_by_id('name').clear()
        self.driver.find_element_by_id('name').send_keys('Edited name')
        self.driver.find_element_by_id('description').clear()
        self.driver.find_element_by_id('description').send_keys(
            'Edited description')
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully edited the department' in success_message

        department = Department.query.get(1)
        self.assertEqual(department.name, 'Edited name')
        self.assertEqual(department.description, 'Edited description')

    def test_delete_department(self):
        """Test that an admin user can delete a department."""
        self.login_admin_user()

        self.driver.find_element_by_id('departments_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('fa-trash').click()
        time.sleep(1)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully deleted the department' in success_message

        self.assertEqual(Deparment.query.count(), 0)


class TestRoles(CreateObjects, TestBase):

    def test_add_role(self):
        """Test that an admin user can add a role."""
        self.login_admin_user()

        self.driver.find_element_by_id('roles_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('btn').click()
        time.sleep(1)

        self.driver.find_element_by_id('name').send_keys(test_role2_name)
        self.driver.find_element_by_id('description').send_keys(
            test_role2_description)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully added a new role' in success_message

        self.assertEqual(Role.query.count(), 2)

    def test_add_existing_role(self):
        """Test that an admin user cannot add a role with a name that
           already exists."""
        self.login_admin_user()

        self.driver.find_element_by_id('roles_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('btn').click()
        time.sleep(1)

        self.driver.find_element_by_id('name').send_keys(test_role1_name)
        self.driver.find_element_by_id('description').send_keys(
            test_role1_description)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        error_message = self.driver.find_element_by_class_name('alert').text
        assert 'Error: Role name already exists' in error_message

        self.assertEqual(Role.query.count(), 1)

    def test_edit_role(self):
        """Test that an admin user can edit a role."""
        self.login_admin_user()

        self.driver.find_element_by_id('roles_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('fa-pencil').click()
        time.sleep(1)

        self.driver.find_element_by_id('name').clear()
        self.driver.find_element_by_id('name').send_keys('Edited name')
        self.driver.find_element_by_id('description').clear()
        self.driver.find_element_by_id('description').send_keys(
            'Edited description')
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully edited the role' in success_message

        role = Role.query.get(1)
        self.assertEqual(role.name, 'Edited name')
        self.assertEqual(role.description, 'Edited description')

    def test_delete_role(self):
        """Test that an admin user can delete a role."""
        self.login_admin_user()

        self.driver.find_element_by_id('roles_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('fa-trash').click()
        time.sleep(1)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully deleted the role' in success_message

        self.assertEqual(Role.query.count(), 0)


class TestEmployees(CreateObjects, TestBase):
    """Test employees model."""

    def test_assign(self):
        """Test that an admin user can assign a role and a department
           to an employee."""
        self.login_admin_user()

        self.driver.find_element_by_id('employees_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('fa-user-plus').click()
        time.sleep(1)

        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully assigned a department and role' in success_message

        employee = Employee.query.get(2)
        self.assertEqual(employee.role.name, test_role1_name)
        self.assertEqual(employee.department.name, test_department1_name)

    def test_reassign(self):
        """Test that an admin user can assign a new role and a new department
           to an employee."""
        department = Department(name=test_department2_name,
                                description=test_department2_description)

        role = Role(name=test_role2_name,
                    description=test_role2_description)

        db.session.add(department)
        db.session.add(role)
        db.session.commit()

        self.login_admin_user()

        self.driver.find_element_by_id('employees_link').click()
        time.sleep(1)

        self.driver.find_element_by_class_name('fa-user-plus').click()
        time.sleep(1)

        select_dept = Select(self.driver.find_element_by_id('department'))
        select_dept.select_by_visible_text(test_department2_name)
        select_role = Select(self.driver.find_element_by_id('role'))
        select_role.select_by_visible_text(test_role2_name)
        self.driver.find_element_by_id('submit').click()
        time.sleep(2)

        success_message = self.driver.find_element_by_class_name('alert').text
        assert 'You have successfully assigned a department and role' in success_message

        employee = Employee.query.get(2)
        self.assertEqual(employee.role.name, test_role2_name)
        self.assertEqual(employee.department.name, test_department2_name)


class TestPermissions(CreateObjects, TestBase):

    def test_permissions_admin_dashboard(self):
        """Test that non-admin users cannot access the admin dashboard."""
        self.login_test_user()

        target_url = self.get_server_url() + url_for('home.admin_dashboard')
        self.driver.get(target_url)

        error_title = self.driver.find_element_by_css_selector('h1').text
        self.assertEqual('403 Error', error_title)
        error_text = self.driver.find_element_by_css_selector('h3').text
        assert 'You do not have sufficient permissions' in error_text

    def test_permissions_list_departments_page(self):
        """Test that non-admin users cannot access the list departments page."""
        self.login_test_user()

        target_url = self.get_server_url() + url_for('admin.list_departments')
        self.driver.get(target_url)

        error_title = self.driver.find_element_by_css_selector('h1').text
        self.assertEqual('403 Error', error_title)
        error_text = self.driver.find_element_by_css_selector('h3').text
        assert 'You do not have sufficient permissions' in error_text

    def test_permissions_add_department_page(self):
        """Test that non-admin users cannot access the add department page."""
        self.login_test_user()

        target_url = self.get_server_url() + url_for('admin.add_department')
        self.driver.get(target_url)

        error_title = self.driver.find_element_by_css_selector('h1').text
        self.assertEqual('403 Error', error_title)
        error_text = self.driver.find_element_by_css_selector('h3').text
        assert 'You do not have sufficient permissions' in error_text

    def test_permissions_list_roles_page(self):
        """Test that non-admin users cannot access the list roles page."""
        self.login_test_user()

        target_url = self.get_server_url() + url_for('admin.list_roles')
        self.driver.get(target_url)

        error_title = self.driver.find_element_by_css_selector('h1').text
        self.assertEqual('403 Error', error_title)
        error_text = self.driver.find_element_by_css_selector('h3').text
        assert 'You do not have sufficient permissions' in error_text

    def test_permissions_add_role_page(self):
        """Test that non-admin users cannot access the add role page."""
        self.login_test_user()

        target_url = self.get_server_url() + url_for('admin.add_role')
        self.driver.get(target_url)

        error_title = self.driver.find_element_by_css_selector('h1').text
        self.assertEqual('403 Error', error_title)
        error_text = self.driver.find_element_by_css_selector('h3').text
        assert 'You do not have sufficient permissions' in error_text

    def test_permissions_list_employees_page(self):
        """Test that non-admin users cannot access the list employees page."""
        self.login_test_user()

        target_url = self.get_server_url() + url_for('admin.list_employees')
        self.driver.get(target_url)

        error_title = self.driver.find_element_by_css_selector('h1').text
        self.assertEqual('403 Error', error_title)
        error_text = self.driver.find_element_by_css_selector('h3').text
        assert 'You do not have sufficient permissions' in error_text

    def test_permissions_assign_employee_page(self):
        """Test that non-admin users cannot access the assign employee page."""
        self.login_test_user()

        target_url = self.get_server_url() + url_for('admin.assign_employee', id=1)
        self.driver.get(target_url)

        error_title = self.driver.find_element_by_css_selector('h1').text
        self.assertEqual('403 Error', error_title)
        error_text = self.driver.find_element_by_css_selector('h3').text
        assert 'You do not have sufficient permissions' in error_text


if __name__ == '__main__':
    unittest.main()
