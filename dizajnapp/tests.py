import os
from django.contrib.admin import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.urls import reverse

from dizajnapp.admin import FlightAdmin, AirwaysPilotAdmin, AirwaysAdmin
from dizajnapp.forms import FlightForm
from dizajnapp.models import Ballon, Airways, Flight, Pilot, AirwaysPilot


class FlightsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_site = AdminSite()
        cls.user = User.objects.create_user(username='testuser', password='testpass')

    def setUp(self):
        self.client.login(username='testuser', password='testpass')

        self.pilot = Pilot.objects.create(
            first_name='PilotName',
            last_name='PilotLastName',
            year_of_birth=2000,
            total_hours=500,
            role='Captain'
        )
        self.ballon = Ballon.objects.create(type='Hot Air', manufacturer_name='XYZ Balloons', max_passengers=4)
        self.airways = Airways.objects.create(name='Airways Inc.', year_founded=2020, coverage_EU=True)

    def test_models(self):
        flight = Flight.objects.create(
            code='ABC123',
            takeoff_airport='Skopje',
            landing_airport='London',
            user=self.user,
            photo='https://cdn.britannica.com/84/158184-050-1D7ADEB5/balloon.jpg',
            ballon=self.ballon,
            pilot=self.pilot,
            airways=self.airways
        )
        self.assertEqual(str(flight), 'ABC123')
        self.assertEqual(flight.user, self.user)
        self.assertEqual(flight.ballon, self.ballon)
        self.assertEqual(flight.pilot, self.pilot)
        self.assertEqual(flight.airways, self.airways)

        airways_pilot = AirwaysPilot.objects.create(pilot=self.pilot, airways=self.airways)
        self.assertEqual(str(airways_pilot), 'PilotName PilotLastName - Airways Inc.')

        self.assertEqual(str(self.pilot), 'PilotName PilotLastName')
        self.assertEqual(str(self.ballon), 'Hot Air - XYZ Balloons')
        self.assertEqual(str(self.airways), 'Airways Inc.')

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_flights_view_get_with_login(self):
        response = self.client.get(reverse('flights'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights.html')
        self.assertEqual(len(response.context['flights']), 0)

    def test_flights_view_get_without_login(self):
        self.client.logout()
        response = self.client.get(reverse('flights'), follow=True)
        self.assertRedirects(response, '/admin/login/?next=/flights/')
        self.assertEqual(response.status_code, 200)

    def test_flights_view_post_valid_form(self):
        form_data = {
            'code': 'ABC123',
            'takeoff_airport': 'Skopje',
            'landing_airport': 'London',
            'ballon': self.ballon.id,
            'pilot': self.pilot.id,
            'airways': self.airways.id,
            'user': self.user.id,
        }

        image_path = os.path.join(os.path.dirname(__file__), 'flights', 'balloonclearday.jpg')
        absolute_path = os.path.abspath(image_path)

        photo_file = open(absolute_path, 'rb')
        files = {'photo': SimpleUploadedFile(photo_file.name, photo_file.read(), content_type='image/jpeg')}

        form_data['photo'] = files['photo']

        response = self.client.post(reverse('flights'), data=form_data, files=files, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights.html')
        self.assertIsInstance(response.context['form'], FlightForm)
        self.assertEqual(response.context['flights'].count(), 1)

        saved_flight = Flight.objects.get(code='ABC123')
        self.assertEqual(saved_flight.takeoff_airport, 'Skopje')
        self.assertEqual(saved_flight.landing_airport, 'London')

        self.assertTrue(saved_flight.photo.url)

    def test_flights_view_post_invalid_form(self):
        form_data = {
            'code': 'ABC123',
            'takeoff_airport': 'Skopje',
            'landing_airport': '',  # Invalid field, should trigger form validation error
            'ballon': self.ballon.id,
            'pilot': self.pilot.id,
            'airways': self.airways.id,
            'user': self.user.id,
        }

        response = self.client.post(reverse('flights'), data=form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'flights.html')
        self.assertIsInstance(response.context['form'], FlightForm)
        self.assertEqual(list(response.context['flights']), [])
        self.assertFormError(response, 'form', 'landing_airport', 'This field is required.')

    def test_flight_admin(self):
        admin = FlightAdmin(model=Flight, admin_site=self.admin_site)
        user_without_permission = User.objects.create_user(username='testuser2', password='testpass')
        change_permission = Permission.objects.get(codename='change_flight')
        user_without_permission.user_permissions.add(change_permission)
        self.assertEqual(admin.exclude, ('user',))

        request = self.client.get(reverse('admin:dizajnapp_flight_add'))
        request.user = self.user
        flight = Flight(code='ABC123', takeoff_airport='Skopje', landing_airport='London',
                        photo='../data/flights/balloonclearday.jpg', ballon=self.ballon, pilot=self.pilot,
                        airways=self.airways, user=self.user)
        admin.save_model(request, flight, None, None)
        self.assertEqual(flight.user, self.user)

        request = self.client.get(reverse('admin:dizajnapp_flight_change', args=[flight.pk]))
        request.user = self.user
        self.assertTrue(admin.has_change_permission(request, flight))
        request.user = user_without_permission
        self.assertFalse(admin.has_change_permission(request, flight))

        request = self.client.get(reverse('admin:dizajnapp_flight_delete', args=[flight.pk]))
        request.user = self.user
        self.assertFalse(admin.has_delete_permission(request, flight))

    def test_airways_admin(self):
        admin = AirwaysAdmin(model=Airways, admin_site=self.admin_site)
        self.assertEqual(admin.list_display, ("name",))
        self.assertEqual(admin.inlines, [AirwaysPilotAdmin])

    def test_flight_form_valid(self):
        form_data = {
            'code': 'ABC123',
            'takeoff_airport': 'Skopje',
            'landing_airport': 'London',
            'ballon': self.ballon.id,
            'pilot': self.pilot.id,
            'airways': self.airways.id,
            'user': self.user.id,
        }

        form = FlightForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_flight_form_invalid(self):
        form_data = {
            'code': 'ABC123',
            'takeoff_airport': 'Skopje',
            'landing_airport': '',  # Invalid field, should trigger form validation error
            'ballon': self.ballon.id,
            'pilot': self.pilot.id,
            'airways': self.airways.id,
            'user': self.user.id,
        }

        form = FlightForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['landing_airport'], ['This field is required.'])
