from django.test import TestCase
from django.test import Client
from django.urls import reverse
from .models import Medicines, Promocode, Sale
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from pharmacy.views import *
from django.core.exceptions import ValidationError

class RegistrationFormTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

    def test_registration_form_valid(self):
        form_data = {
            'username': 'user',
            'first_name': 'User',
            'last_name': 'User',
            'age': 30,
            'phone': '+375(29)1262368',
            'address': 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword111',
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_password_mismatch(self):
        form_data = {
            'username': 'user',
            'first_name': 'User',
            'last_name': 'User',
            'age': 30,
            'phone': '+375(29)1262368',
            'address': 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword112',
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['The two password fields didn’t match.'])


class UserLoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='client', password='password', status='client', phone = "+375(29)1214121", first_name = "Hdhdj", last_name="djksjdk", address = "ul.shjhds1", age=30)
        
    def test_login_auth_user(self):
        response = self.client.post(reverse('login'), {'username': 'client', 'password': 'password'})
        self.assertEqual(response.status_code, 200)

    def test_login_template(self):
        response = self.client.get(reverse('login'))
        self.assertTemplateUsed(response, 'login.html')

    def test_login_success_url(self):
        view = UserLoginView()
        self.assertEqual(view.get_success_url(), reverse('home'))

class RegistrationTest(TestCase):
    def test_get_view(self):
        client = Client()
        response = client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration.html')

    def test_post_valid_data(self):
        data = {
            'username': 'user',
            'first_name': 'User',
            'last_name': 'User',
            'age': 30,
            'phone': '+375(29)1262368',
            'address': 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword111',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(User.objects.filter(username='user').exists())

    def test_post_invalid_age(self):
        client = Client()
        data = {
            'username': 'user',
            'first_name': 'User',
            'last_name': 'User',
            'age': 10,
            'phone': '+375(29)1262368',
            'address': 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword111',
        }
        with self.assertRaises(ValidationError):
            client.post(reverse('register'), data)
        self.assertFalse(User.objects.filter(username='user').exists())

    def test_post_invalid_phone(self):
        client = Client()
        data = {
            'username': 'user',
            'first_name': 'User',
            'last_name': 'User',
            'age': 30,
            'phone': '+375291262368',
            'address': 'Test',
            'password1': 'testpassword111',
            'password2': 'testpassword111',
        }
        with self.assertRaises(ValidationError):
            client.post(reverse('register'), data)
        self.assertFalse(User.objects.filter(username='user').exists())

class UserSaleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='userclient', password='password', status='client', phone = "+375(29)1234567", first_name = "A", last_name="B", address = "test", age=67)
        self.user_staff = User.objects.create(username='userstaff', password='password', status='staff', phone = "+375(29)1234567", first_name = "C", last_name="D", address = "test", age=67)
        self.category = Categories.objects.create(name="Test Category")
        self.supplier = Supplier.objects.create(name="Test Supplier",  address="Test Address", phone="+375(29)1234567")
        self.medicine = Medicines.objects.create(name="Test Medicine 1", cost=100, categories=self.category, suppliers = self.supplier)
        self.department = Department.objects.create(no = 5, address = "test", close = "13:15:24.548638", open = "13:15:24.548638")
        self.depmed = DepartmentMedicine.objects.create(quantity = 3, department = self.department, medicine = self.medicine)
        self.promocode = Promocode.objects.create(code='MED103', discount=10)

    def test_get_auth_client_medic_exists(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('create_order', kwargs={'pk': self.medicine.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'order_create_form.html')

    def test_get_auth_client_medic_nonexist(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('create_order', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_get_auth_staff(self):
        self.client.force_login(self.user_staff)
        response = self.client.get(reverse('create_order', kwargs={'pk': self.medicine.pk}))
        self.assertEqual(response.status_code, 404)

    def test_get_unauth(self):
        response = self.client.get(reverse('create_order', kwargs={'pk': self.medicine.pk}))
        self.assertEqual(response.status_code, 404) 

    def test_post_auth_client_invalid_data(self):
        self.client.force_login(self.user_client)
        
        data = {
            'amount': 300,
            'department': self.department.pk,
            'promocode': self.promocode.code
        }
        
        response = self.client.post(reverse('create_order', kwargs={'pk': self.medicine.pk}), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Выберыце іншае аддзяленне аптэкі або дачакайцеся новай пастаўкі")

    def test_post_auth_client_valid_data(self):
        self.client.force_login(self.user_client)
        
        data = {
            'amount': 1,
            'department': self.department.pk,
            'promocode': self.promocode.code
        }
        
        response = self.client.post(reverse('create_order', kwargs={'pk': self.medicine.pk}), data)
        self.assertEqual(response.status_code, 302) 
        self.assertTrue(Sale.objects.filter(user=self.user_client, medicine=self.medicine).exists())


class SpecificOrderViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='userclient', password='password', status='client', phone = "+375(29)1234567", first_name = "A", last_name="B", address = "test", age=67)
        self.user_staff = User.objects.create(username='userstaff', password='password', status='staff', phone = "+375(29)1234567", first_name = "C", last_name="D", address = "test", age=67)
        self.category = Categories.objects.create(name="Test Category")
        self.supplier = Supplier.objects.create(name="Test Supplier",  address="Test Address", phone="+375(29)1234567")
        self.medicine = Medicines.objects.create(name="Test Medicine 1", cost=100, categories=self.category, suppliers = self.supplier)
        self.department = Department.objects.create(no = 5, address = "test", close = "13:15:24.548638", open = "13:15:24.548638")
        self.depmed = DepartmentMedicine.objects.create(quantity = 3, department = self.department, medicine = self.medicine)
        self.promocode = Promocode.objects.create(code='MED103', discount=10)
        self.order = Sale.objects.create(department = self.department, promocode = self.promocode, user = self.user_client, medicine = self.medicine, quantity = 3, price = 15, price_prom = 15)

    def test_get_auth_user_and_order_nonexist(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('user_order', kwargs={'pk': self.user_client.pk, 'jk': 999}))
        self.assertEqual(response.status_code, 404)

    def test_get_unauth(self):
        response = self.client.get(reverse('user_order', kwargs={'pk': self.user_client.pk, 'jk': self.order.id}))
        self.assertEqual(response.status_code, 404)  

    def test_post_auth_user_and_order_exists_invalid_data(self):
        self.client.force_login(self.user_client)
        response = self.client.post(reverse('user_order', kwargs={'pk': self.user_client.pk, 'jk': self.order.id}), {'confirm': True})
        self.assertEqual(response.status_code, 405)  

    def test_post_auth_user_and_order_nonexist(self):
        self.client.force_login(self.user_client)
        response = self.client.post(reverse('user_order', kwargs={'pk': self.user_client.pk, 'jk': 999}), {'confirm': True})
        self.assertEqual(response.status_code, 405)

    def test_post_unauth(self):
        response = self.client.post(reverse('user_order', kwargs={'pk': self.user_client.pk, 'jk': self.order.id}), {'confirm': True})
        self.assertEqual(response.status_code, 405)  

class MedicinesListViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('medicines')
        self.category = Categories.objects.create(name="Test Category")
        self.supplier = Supplier.objects.create(name="Test Supplier",  address="Test Address", phone="+375(29)1234567")
        self.medicine1 = Medicines.objects.create(name="Test Medicine 1", cost=100, categories=self.category, suppliers = self.supplier)
        self.medicine2 = Medicines.objects.create(name="Test Medicine 2", cost=200, categories=self.category, suppliers = self.supplier)

    def test_view_with_no_search_query(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Medicine 1")
        self.assertContains(response, "Test Medicine 2")
        self.assertNotContains(response, "Тавар адсутнічае")

    def test_view_with_search_query_found(self):
        response = self.client.get(self.url, {'search': 'Test Medicine 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Medicine 1")
        self.assertNotContains(response, "Test Medicine 2")
        self.assertNotContains(response, "Тавар адсутнічае")

    def test_view_with_search_query_not_found(self):
        response = self.client.get(self.url, {'search': 'Nonexistent Medicine'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Тавар адсутнічае")
        self.assertNotContains(response, "Test Medicine 1")
        self.assertNotContains(response, "Test Medicine 2")

    def test_view_with_price_filter(self):
        response = self.client.get(self.url, {'min_cost': '150', 'max_cost': '250'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Test Medicine 1")
        self.assertContains(response, "Test Medicine 2")
        self.assertNotContains(response, "Товар отсутствует")

    def test_view_with_empty_price_filter(self):
        response = self.client.get(self.url, {'min_cost': '', 'max_cost': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Medicine 1")
        self.assertContains(response, "Test Medicine 2")
        self.assertNotContains(response, "Товар отсутствует")

class ReviewCreateViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='userclient', password='password', status='client', phone = "+375(29)1234567", first_name = "A", last_name="B", address = "test", age=67)

    def test_create_review_authenticated_client(self):
        self.client.force_login(self.user_client)
        data = {
            'title': 'Test Review',
            'rating': 5,
            'text': 'This is a test review.'
        }
        response = self.client.post(reverse('add_review'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Review.objects.filter(title='Test Review', user=self.user_client).exists())

    def test_create_review_unauthenticated_user(self):
        data = {
            'title': 'Test Review',
            'rating': 5,
            'text': 'This is a test review.'
        }
        response = self.client.post(reverse('add_review'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')  # Assuming login URL is /login/
        self.assertFalse(Review.objects.filter(title='Test Review').exists())
        

class ReviewEditViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='userclient', password='password', status='client', phone = "+375(29)1234567", first_name = "A", last_name="B", address = "test", age=67)
        self.review = Review.objects.create(title='Original Title', rating=4, text='Original text', user=self.user_client)

    def test_edit_review_authenticated_client(self):
        self.client.force_login(self.user_client)
        data = {
            'title': 'Updated Title',
            'rating': 3,
            'text': 'Updated text'
        }
        response = self.client.post(reverse('edit_review', kwargs={'review_id': self.review.id}), data)
        self.assertEqual(response.status_code, 302)
        self.review.refresh_from_db()
        self.assertEqual(self.review.title, 'Updated Title')
        self.assertEqual(self.review.rating, 3)
        self.assertEqual(self.review.text, 'Updated text')

class ReviewDeleteViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_client = User.objects.create(username='userclient', password='password', status='client', phone = "+375(29)1234567", first_name = "A", last_name="B", address = "test", age=67)
        self.review = Review.objects.create(title='Test Title', rating=4, text='Test text', user=self.user_client)

    def test_delete_review_authenticated_client(self):
        self.client.force_login(self.user_client)
        response = self.client.get(reverse('delete_review', kwargs={'review_id': self.review.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())


