from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.decorators import login_required, permission_required
from sedUI.forms import RegistrationForm1, RegistrationForm2, RegistrationScoutForm1, RegistrationScoutForm2, RegistrationVolunteerForm1, RegistrationVolunteerForm2, RegistrationPaymentForm, ContactEmailForm, BadgeForm

urlpatterns=[
	url(r'^$', views.IndexView.as_view(), name='index'),
	url(r'^about/?$', views.AboutView.as_view(), name='about'),
	url(r'^contact/?$', views.ContactView.as_view([ContactEmailForm]), name='contact'),
	url(r'^contactConfirmation/?$', views.ContactConfirmationView.as_view(), name='contactConfirmation'),
	url(r'^badge/?$', views.BadgeView.as_view([BadgeForm]), name='badge'),
	url(r'^allbadges/?$', login_required(views.AllBadgesView.as_view()), name='allbadges'),

	## Registration Process Pages
	url(r'^registration/?$', views.RegistrationView.as_view(), name='registration'),
	url(r'^registrationIssue/?$', views.RegistrationIssueView.as_view(), name='registrationIssue'),

	## Initial Registration Flow
	url(r'^registration_initial/?$', views.RegistrationWizard.as_view([RegistrationForm1, RegistrationForm2]), name='initial_registration'),

	## Scout Registration Flow
	url(r'^registration_scout/?$', views.RegistrationScoutWizard.as_view([RegistrationScoutForm1, RegistrationScoutForm2]), name='scout_registration'),
	
	## Volunteer Registration Flow
	url(r'^registration_volunteer/?$', views.RegistrationVolunteerWizard.as_view([RegistrationVolunteerForm1, RegistrationVolunteerForm2]), name='volunteer_registration'),
	
	## Payment Registration flow
	url(r'^registration_payment/?$', views.RegistrationLastWizard.as_view([RegistrationPaymentForm]), name='payment_registration'),
	
	## Confirmation Registration 
	url(r'^registration_confirmation/?$', views.RegistrationConfirmation.as_view(), name="confirmation_registration"),

	url(r'^scouts/?$', login_required(views.ScoutView.as_view()), name='scout'),
	url(r'^scout_detail/(?P<scout_id>[a-zA-Z0-9\-._]+)/?$', login_required(views.ScoutDetailView.as_view()), name='scout_detail/'),

	## Course Pages
	url(r'^courses/?$', views.CourseView.as_view(), name='course'),
	url(r'^course_detail/(?P<course_id>[a-zA-Z0-9\-._]+)/?$', views.CourseDetailView.as_view(), name='course_detail/'),

	url(r'^workshops/?$', login_required(views.WorkshopView.as_view()), name='workshop'),
	url(r'^workshop_detail/(?P<workshop_id>[a-zA-Z0-9\-._]+)/?$', login_required(views.WorkshopDetailView.as_view()), name='workshop_detail/'),
	

	url(r'^profile/?$', login_required(views.ProfileView.as_view()), name='profiles'),

	## url scouts function:
	## Event Checkin/Checkout
	url(r'^scout_detail/(?P<scout_id>[a-zA-Z0-9\-._]+)/checkin/?$', login_required(views.event_checkin), name='scout_event_checkin/'),
	url(r'^scout_detail/(?P<scout_id>[a-zA-Z0-9\-._]+)/checkout/?$', login_required(views.event_checkout), name='scout_event_checkout/'),

	## Workshop Checkin/Checkout
	url(r'^scout_detail/(?P<scout_id>[a-zA-Z0-9\-._]+)/workshop_checkin/?$', login_required(views.workshop_checkin), name='scout_workshop_checkin/'),
	url(r'^scout_detail/(?P<scout_id>[a-zA-Z0-9\-._]+)/workshop_completed/?$', login_required(views.workshop_completed), name='scout_workshop_completed/'),
	url(r'^scout_detail/(?P<scout_id>[a-zA-Z0-9\-._]+)/workshop_checkout/?$', login_required(views.workshop_checkout), name='scout_workshop_checkout/'),

	#might need to look into class based view for later interation
    url(r'^login/?$', auth_views.login, {'template_name': 'sedUI/pages/login.html'}, name='login'),
    url(r'^logout/?$', auth_views.logout, {'template_name': 'sedUI/pages/logged_out.html'}, name='logout'),

]
