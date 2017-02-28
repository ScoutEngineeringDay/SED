from django.shortcuts import render, render_to_response, redirect, HttpResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Course, Scout, Workshop, Session, Instructor, AboutPage, HomePage, Checkout, MailPayment
import os
from django.views import generic
from django.core.urlresolvers import reverse
from django.views.generic import View
from .forms import RegistrationForm1, RegistrationForm2, RegistrationForm3, RegistrationForm4, ContactEmailForm, BadgeForm
from formtools.wizard.views import WizardView
from formtools.wizard.views import SessionWizardView, CookieWizardView
import datetime
import re
import pytz
import stripe
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail, EmailMessage
from django.core.management.utils import get_random_secret_key

FORMS = [("citizenship", RegistrationForm1),
         ("scout_info", RegistrationForm2),
         ("selection", RegistrationForm3),
         ("payment", RegistrationForm4)]

# Create your views here.
class IndexView(generic.TemplateView):
	template_name='sedUI/pages/index.html'
	def get(self, request, *args, **kwargs):
		HomePage_object=HomePage.objects.latest('homepage_id')
		aboutPage = AboutPage.objects.latest('aboutPage_id')
		img_fileNames = []
		#Add first image
		img_fileNames.append(os.path.join('img/images/', '00001.jpg'))
		# for filename in os.listdir("sed/sedUI/static/img/homeImages"):    # Use if running on AWS Server
		for filename in os.listdir("sedUI/static/img/homeImages"):          # Use if running on Local Machine
			img_fileNames.append(os.path.join('img/homeImages/', filename))
		return render(request, 'sedUI/pages/index.html', {"fileNames" : img_fileNames, "HomePage": HomePage_object,'aboutPage' : aboutPage})

class RegistrationIssueView(generic.TemplateView):
    template_name = 'sedUI/pages/registrationIssue.html'

class ContactConfirmationView(generic.TemplateView):
    template_name = 'sedUI/pages/contactConfirmation.html'

class ContactView(SessionWizardView):
    form_list=[ContactEmailForm]
    template_name = 'sedUI/pages/contact.html'

    def done(self, form_list, **kwargs):
        print("send")
        contact_send_email(form_list)
        return render_to_response('sedUI/pages/contactConfirmation.html', {'form_data': [form.cleaned_data for form in form_list]})

def contact_send_email(form_list):
    form_data =[form.cleaned_data for form in form_list]
    message=("Contact Email: "+ form_data[0]["email_address"]+"\n\nContact name: "+form_data[0]["contact_name"]+"\n\nMessage:\n"+form_data[0]["message"])
    #send_mail(subject, message, from, to)
    send_mail(form_data[0]["message_subject"], message, form_data[0]["email_address"], [settings.EMAIL_HOST_USER], fail_silently=False)
    return form_data

def login(request):
    return render(request, 'sedUI/pages/basic.html')

def loginOrRegister(request):
    return render(request, 'sedUI/pages/loginOrRegister.html')

class CourseView(generic.ListView):
    template_name = 'sedUI/pages/courses.html'
    context_object_name = 'all_courses'
    def get_queryset(self):
        return Course.objects.all()

class CourseDetailView(generic.ListView):
    template_name = 'sedUI/pages/course_detail.html'
    context_object_name = 'course'
    def get_queryset(self):
        return Course.objects.get(course_id=self.kwargs['course_id'])

    def get_context_data(self, **kwargs):
        ctx=super(CourseDetailView, self).get_context_data(**kwargs)
        #ctx['instructor2']=Instructor2.objects.get(instructor_id=str(Workshop2.objects.get(course_id=str(self.get_queryset().course_id), workshop_time="AM").instructor_id))
        try:
            ctx['instructorAM']=Instructor.objects.get(instructor_id=Workshop.objects.get(course_id=self.get_queryset().course_id, workshop_time="AM").instructor_id)
        except:
            ctx['instructorAM']=None
        try:
            ctx['instructorPM']=Instructor.objects.get(instructor_id=Workshop.objects.get(course_id=self.get_queryset().course_id, workshop_time="PM").instructor_id)
        except:
            ctx['instructorPM']=None
        try:
            ctx['instructorFULL']=Instructor.objects.get(instructor_id=Workshop.objects.get(course_id=self.get_queryset().course_id, workshop_time="FULL").instructor_id)
        except:
            ctx['instructorFULL']=None
        return ctx

class ScoutView(generic.ListView):
    template_name = 'sedUI/pages/scouts.html'
    context_object_name = 'all_scouts'

    def get_queryset(self):
        return Scout.objects.all()

class ScoutDetailView(generic.ListView):
    template_name = 'sedUI/pages/scout_detail.html'
    context_object_name='scout'
    def get_queryset(self):
        return Scout.objects.get(scout_id=self.kwargs['scout_id'])

    def get_context_data(self, **kwargs):
        ctx=super(ScoutDetailView, self).get_context_data(**kwargs)
        #ctx['instructor']=Instructor2.objects.get(instructor_id=str(Workshop2.objects.get(course_id=str(self.get_queryset().course_id), workshop_time="AM").instructor_id))
        try:
            ctx['session']=Session.objects.get(scout_id=self.get_queryset().scout_id)
        except:
            ctx['session']=None
        return ctx

def event_checkin(request, scout_id):
    try:
        scout=Scout.objects.get(scout_id=scout_id, scout_year=datetime.datetime.now().year)
        if(scout.scout_status=="UNDERWAY" or scout.scout_status=='EVENT_CHECKOUT'):
            scout.scout_status='EVENT_CHECKIN'
            scout.save()
            session=Session.objects.get(scout_id=scout_id, session_year=scout.scout_year)
            session.event_checkin=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        else:
            return HttpResponse('Scout has already check into the event')
    except:
        return HttpResponse('Scout no longer exist in database')

def event_checkout(request, scout_id):
    try:
        scout=Scout.objects.get(scout_id=scout_id, scout_year=datetime.datetime.now().year)
        if(scout.scout_status=='EVENT_CHECKIN' or scout.scout_status=='WORKSHOP1_CHECKOUT' or scout.scout_status=='WORKSHOP2_CHECKOUT'):
            scout.scout_status='EVENT_CHECKOUT'
            scout.save()
            session=Session.objects.get(scout_id=scout_id, session_year=scout.scout_year)
            session.event_checkout=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        else:
            return HttpResponse('Scout has not been Check into the Event or Checkout of Workshops yet')
    except:
        return HttpResponse('Scout no longer exist in database')

def workshop_checkin(request, scout_id):
    try:
        scout=Scout.objects.get(scout_id=scout_id, scout_year=datetime.datetime.now().year)
        session=Session.objects.get(scout_id=scout_id, session_year=scout.scout_year)
        if(scout.scout_status=='EVENT_CHECKIN'):
            scout.scout_status='WORKSHOP1_CHECKIN'
            scout.save()
            session.workshop1_status='IN PROGRESS'
            session.workshop1_checkin=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        elif(scout.scout_status=='WORKSHOP1_CHECKOUT' and session.workshop2_id != '0'):
            scout.scout_status='WORKSHOP2_CHECKIN'
            scout.save()
            session.workshop1_status='IN PROGRESS'
            session.workshop2_checkin=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        else:
            return HttpResponse('Scout has not been Check into the Event or Checkout of Workshops or have already Checkout of Event')
    except:
        return HttpResponse('Scout no longer exist in database')

def workshop_completed(request, scout_id):
    try:
        scout=Scout.objects.get(scout_id=scout_id, scout_year=datetime.datetime.now().year)
        session=Session.objects.get(scout_id=scout_id, session_year=scout.scout_year)
        if(scout.scout_status=='WORKSHOP1_CHECKIN'):
            scout.scout_status='WORKSHOP1_CHECKOUT'
            scout.save()
            session.workshop1_status="COMPLETE"
            session.workshop1_checkout=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        elif(scout.scout_status=='WORKSHOP2_CHECKIN'):
            scout.scout_status='WORKSHOP2_CHECKOUT'
            scout.save()
            session.workshop2_status="COMPLETE"
            session.workshop2_checkout=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        else:
            return HttpResponse('Scout has not been Check into the Event or Checkout of Workshops or have already Checkout of Event')
    except:
        return HttpResponse('Scout no longer exist in database')

def workshop_checkout(request, scout_id):
    try:
        scout=Scout.objects.get(scout_id=scout_id, scout_year=datetime.datetime.now().year)
        session=Session.objects.get(scout_id=scout_id, session_year=scout.scout_year)
        if(scout.scout_status=='WORKSHOP1_CHECKIN'):
            scout.scout_status='WORKSHOP1_CHECKOUT'
            scout.save()
            session.workshop1_status="INCOMPLETE"
            session.workshop1_checkout=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        elif(scout.scout_status=='WORKSHOP2_CHECKIN'):
            scout.scout_status='WORKSHOP2_CHECKOUT'
            scout.save()
            session.workshop2_status="INCOMPLETE"
            session.workshop2_checkout=datetime.datetime.now()
            session.save()
            return HttpResponseRedirect(reverse('scout_detail/', args=(scout_id,)))
        else:
            return HttpResponse('Scout has not been Check into the Event or Checkout of Workshops or have already Checkout of Event')
    except:
        return HttpResponse('Scout no longer exist in database')

class ReportView(generic.TemplateView):
    template_name = 'sedUI/pages/reportAnalysis.html'


class ProfileView(generic.TemplateView):
    template_name = 'sedUI/pages/profile.html'

class AboutView(generic.TemplateView):
    template_name='sedUI/pages/about.html'
    # context_object_name = 'all_courses'
    def get(self, request, *args, **kwargs):
    	aboutPage = AboutPage.objects.latest('aboutPage_id')
        all_courses = Course.objects.all()
        left_items = all_courses[:(len(all_courses)+1)/2]
        right_items = all_courses[(len(all_courses)+1)/2:]
        current_datetime = datetime.datetime.now()
        isOpen=checkOpenDate()
        # if (current_datetime>aboutPage.registrationOpenDate) and (current_datetime<aboutPage.saveDate):
        #     isOpen=True
        # else:
        #     isOpen=False
        context = {
            'all_courses' : all_courses,
            'left_items' : left_items,
            'right_items' : right_items,
            'aboutPage' : aboutPage,
            'isOpen' : isOpen
        }
    	return render(request, 'sedUI/pages/about.html', context);

class BadgeView(SessionWizardView):
    form_list=[BadgeForm]
    template_name = 'sedUI/pages/getBadge.html'

    def done(self, form_list, **kwargs):
        form_data=self.get_cleaned_data_for_step('0')
        confirmation_id=form_data["confirmation_id"]
        try:
            scout_data=Scout.objects.get(confirmation_id=confirmation_id)
            session_data=Session.objects.get(scout_id=scout_data.scout_id)
            course_1=Course.objects.get(course_id=(Workshop.objects.get(workshop_id=session_data.workshop1_id).course_id))
            course_2=None
            location_1=Location.objects.get(location_id=(Workshop.objects.get(workshop_id=session_data.workshop1_id).location_id))
            if(session_data.workshop2_id=='0' or session_data.workshop2_id==None):
                course_2=Course.objects.get(course_id=(Workshop.objects.get(workshop_id=session_data.workshop2_id).course_id))
                location_2=Location.objects.get(location_id=(Workshop.objects.get(workshop_id=session_data.workshop1_id).location_id))
            else:
                course_2=None
                location_2=None
        except Scout.DoesNotExist:
            scout_data = None
            course_1 = None
            course_2 = None
            location_1 = None
            location_2 = None
        print("get")
        return render_to_response('sedUI/pages/showBadge.html',
            {'form_data': [form.cleaned_data for form in form_list],
                'scout': scout_data,
                'workshop_1': course_1,
                'workshop_2': course_2,
                'location_1': location_1,
                'location_2': location_2
            }
        )

class RegistrationWizard(SessionWizardView):
    form_list = [RegistrationForm1, RegistrationForm2, RegistrationForm3, RegistrationForm4]
    template_name = 'sedUI/pages/registration_form.html'

    def get_context_data(self, **kwargs):
        ctx=super(RegistrationWizard, self).get_context_data(**kwargs)
        #ctx['instructor']=Instructor2.objects.get(instructor_id=str(Workshop2.objects.get(course_id=str(self.get_queryset().course_id), workshop_time="AM").instructor_id))
        try:
            ctx['isOpen']=checkOpenDate()
            ctx['payment']=MailPayment.objects.latest('mailPayment_id')
            ctx['checkout']=Checkout.objects.latest('checkout_id')
        except:
            ctx['isOpen']=checkOpenDate()
            ctx['payment']=None
            ctx['checkout']=None
        return ctx

    def render(self, form=None, **kwargs):
        form = form or self.get_form()
        if self.steps.current=='3':
            context = self.get_context_data(form=form, **kwargs)
            return self.render_to_response(context)
        context = self.get_context_data(form=form, **kwargs)
        return self.render_to_response(context)

    def render_next_step(self, form, **kwargs):
        """
        This method gets called when the next step/form should be rendered.
        `form` contains the last/current form.
        """
        # get the form instance based on the data from the storage backend
        # (if available).

        # check citizen status
        if(self.steps.current=='0'):
            data=self.get_cleaned_data_for_step('0')
            if(data["citizenship"]=='No'):
                return redirect(reverse('registrationIssue'))
        # run default render_next_step
        next_step = self.steps.next
        new_form = self.get_form(
            next_step,
            data=self.storage.get_step_data(next_step),
            files=self.storage.get_step_files(next_step),
        )

        # change the stored current step
        self.storage.current_step = next_step
        return self.render(new_form, **kwargs)

    def done(self, form_list, **kwargs):
        course_1=None
        course_2=None
        scout_data=self.get_cleaned_data_for_step('1')
        workshop_data=self.get_cleaned_data_for_step('2')
        session_data=self.get_cleaned_data_for_step('3')

        if(session_data["payment_method"]=="Pay_Online"):
        	stripeCall(self.request)

        # store into database scout table
        scout = Scout(scout_first_name=scout_data["first_name"],
            scout_last_name=scout_data["last_name"],
            unit_number=scout_data["unit_number"],
            scout_phone=scout_data["phone"],
            scout_email=scout_data["email"],
            emergency_first_name=scout_data["emergency_first_name"],
            emergency_last_name=scout_data["emergency_last_name"],
            emergency_phone=scout_data["emergency_phone"],
            emergency_email=scout_data["emergency_email"],
            scout_type=scout_data["affiliation"],
            scout_photo=scout_data["photo"],
            scout_medical=scout_data["medical_notes"],
            scout_allergy=scout_data["allergy_notes"],
            scout_status="UNDERWAY",
            scout_year=str(datetime.datetime.now().year)
            )
        scout.save()
        # # store into database session table
        #filter courses
        workshop1_data=str(workshop_data["morning_subject"]).split('-')
        if(workshop1_data[1]=="FULL"):
            session = Session(
            scout_id=scout.scout_id,
            payment_method=session_data["payment_method"],
            payment_amount="40.00",
            workshop1_id=Workshop.objects.get(course_id=Course.objects.get(course_name=workshop1_data[0]).course_id, workshop_time="FULL").workshop_id,
            workshop1_status="IN PROGRESS",
            confirmation_timestamp=datetime.datetime.now(),
            session_year=str(datetime.datetime.now().year)
            )
            session.save()
            course_1=Course.objects.get(course_id=(Workshop.objects.get(workshop_id=session.workshop1_id).course_id))
            course_2=None
            location_1=Location.objects.get(location_id=Workshop.objects.get(workshop_id=session.workshop1_id).location_id)
            location_2=None
        else:
            #if there is a PM CLass
            workshop2_data=None
            if(workshop_data["evening_subject"]!=None):
                workshop2_data=str(workshop_data["evening_subject"]).split('-')
                session = Session(
                scout_id=scout.scout_id,
                payment_method=session_data["payment_method"],
                payment_amount="40.00",
                workshop1_id=Workshop.objects.get(course_id=Course.objects.get(course_name=workshop1_data[0]).course_id, workshop_time="AM").workshop_id,
                workshop2_id=Workshop.objects.get(course_id=Course.objects.get(course_name=workshop2_data[0]).course_id, workshop_time="PM").workshop_id,
                workshop1_status="IN PROGRESS",
                workshop2_status="IN PROGRESS",
                confirmation_timestamp=datetime.datetime.now(),
                session_year=str(datetime.datetime.now().year)
                )
                session.save()
                course_1=Course.objects.get(course_id=(Workshop.objects.get(workshop_id=session.workshop1_id).course_id))
                course_2=Course.objects.get(course_id=(Workshop.objects.get(workshop_id=session.workshop2_id).course_id))
                location_1=Location.objects.get(location_id=Workshop.objects.get(workshop_id=session.workshop1_id).location_id)
                location_2=Location.objects.get(location_id=Workshop.objects.get(workshop_id=session.workshop2_id).location_id)
            # Error issue
            else:
                workshop2_data=None
                print("Error")
                session = Session(
                scout_id=scout.scout_id,
                payment_method=session_data["payment_method"],
                payment_amount="40.00",
                workshop1_id=Workshop.objects.get(course_id=Course.objects.get(course_name=workshop1_data[0]).course_id, workshop_time="AM").workshop_id,
                workshop1_status="IN PROGRESS",
                confirmation_timestamp=datetime.datetime.now(),
                session_year=str(datetime.datetime.now().year)
                )
                session.save()
                course_1=Course.objects.get(course_id=(Workshop.objects.get(workshop_id=session.workshop1_id).course_id))
                course_2=None
                location_1=Location.objects.get(location_id=Workshop.objects.get(workshop_id=session.workshop1_id).location_id)
                location_2=None
        all_models_dict ={
        	'form_data': [form.cleaned_data for form in form_list],
    		'scout': scout,
    		'session': session,
    		'workshop_1': course_1,
            'workshop_2': course_2,
            'location_1': location_1,
            'location_2': location_2
        }
        confirmation_timestamp=session.confirmation_timestamp
        confirmation_send_email(form_list, scout.scout_id, str(scout.confirmation_id))
        return render_to_response('sedUI/pages/registrationConfirmation.html', {'form_data': [form.cleaned_data for form in form_list],
    		'scout': scout,
    		'session': session,
    		'workshop_1': course_1,
            'workshop_2': course_2,
            'location_1': location_1,
            'location_2': location_2
        	})

def stripeCall(request):
	# Set your secret key: remember to change this to your live secret key in production
	# See your keys here: https://dashboard.stripe.com/account/apikeys
	stripe.api_key = Checkout.objects.latest('checkout_id').private_key

	# Token is created using Stripe.js or Checkout!
	# Get the payment token submitted by the form:
	token = request.POST['stripeToken']

	# Charge the user's card:
	charge = stripe.Charge.create(
		amount=4000,
		currency="usd",
		description="Example charge",
		source=token,
	)

def confirmation_send_email(form_list, scout_id, confirmation_id):
    message = None
    scout_info=None
    emergency_info=None
    payment_timestamp=None
    form_data =[form.cleaned_data for form in form_list]
    print("sending")
    #formatting data to be transmit through the message
    scout_info = ("\n\nScout Information:\n\tScout ID: "+str(scout_id)+"\n\tScout Name: "+str(form_data[1]["first_name"])+" "+str(form_data[1]["last_name"])+"\n\tScout type: "+str(form_data[1]["affiliation"])+"\n\tUnit Number:"+str(form_data[1]["unit_number"])+"\n\nScout Contact Information:\n\tPhone Number: "+str(form_data[1]["phone"])+"\n\tEmail: "+str(form_data[1]["email"]))
    emergency_info = ("\n\nEmergency Contact:\n\tEmergency Name:"+str(form_data[1]["emergency_first_name"])+" "+str(form_data[1]["emergency_last_name"])+"\n\tEmergency Phone: "+str(form_data[1]["emergency_phone"]))
    # course_info=("\n\nCourses:\tClass 1:"+form_data[2]["morning_subject"]+"\tClass 2:"+form_data[2]["evening_subject"])
    payment_timestamp=("\n\nPayment Method: "+str(form_data[3]["payment_method"]))
    message = "Hello,"+scout_info+emergency_info+payment_timestamp+"\n\nIf there is any information that is mistaken please contact us.\n To reprint Badge, go to Get Badge and enter your confirmation number: "+confirmation_id+"\n\nThank you,\n\t Scout Engineering Day Development Team"


    email = EmailMessage(
        'Confirmation Message',
        message,
        settings.EMAIL_HOST_USER,
        [form_data[1]["email"]],
        )
    email.send(fail_silently=False)
    #send_mail(subject, message, from, to)
    # send_mail('Confirmation', str(form_data), settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=False)
    return form_data

def checkOpenDate():
    isOpen=False
    registration_force_closed=True
    aboutPage = AboutPage.objects.latest('aboutPage_id')
    current_datetime= str(datetime.datetime.now())
    if(aboutPage.forceClosed==True):
        print("registration forced closed")
        isOpen="ForcedClosed"
    elif(current_datetime<aboutPage.saveDate and current_datetime>aboutPage.registrationOpenDate):
        print("registration open")
        isOpen="Opened"
    else:
        print("registration closed")
        isOpen="Closed"
    return isOpen