from django.shortcuts import render,redirect
from django.shortcuts import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import Paymentform, Propform, Requestform, Tenantform,Compform
from django.views.decorators.csrf import csrf_protect
from .models import Tenants, Booked, Payment, Units, Issues, Admin
from django.core.mail import send_mail
from django.db import IntegrityError
from django.db.models import Sum
from datetime import datetime
from calendar import monthrange
from django.http import HttpResponse
from django.conf import settings
from django.http import JsonResponse
import locale
from django.core.serializers import serialize
from django.http import JsonResponse
import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import MultipleObjectsReturned

locale.setlocale(locale.LC_MONETARY, 'en_US.UTF-8')

def index(request):
    return render(request, 'render/index.html', {})

def user_logout(request):
    logout(request)
    return redirect('home')  

def delete_unit(request, unit_id):
    try:
        unit = Units.objects.get(pk=unit_id)
        unit.delete()
        return JsonResponse({'success': True})
    except Units.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Unit not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def delete_tent(request, tenant_id):
    try:
        tenant = Tenants.objects.get(pk=tenant_id)
        unit = tenant.assigned_unit
        tenant.delete()

        if unit and not unit.unt_availability:
            unit.unt_availability = True 
            unit.save()  

        return JsonResponse({'success': True})
    except Tenants.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tenant not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def comp_solv(request, issue_id):
    try:
        comp = Issues.objects.get(pk=issue_id)
        comp.delete()    
        return JsonResponse({'success': True})
    except Tenants.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tenant not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    

def home(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        pword = request.POST.get('pass')
        try:
            tenant = Tenants.objects.get(username=uname)
        except MultipleObjectsReturned:  
            messages.error(request, "Authentication failed. Please check your credentials.")
        except Tenants.DoesNotExist:
            tenant = None
        if tenant is not None and tenant.check_password(pword):
            login(request, tenant, backend='coreapp.backend.TenantBackend')
            return redirect(reverse('tnt_hom') + f'?username={uname}')

        user = authenticate(request, username=uname, password=pword)
        if user is not None:
            login(request, user)
            return redirect('admins')

        messages.error(request, "Authentication failed. Please check your credentials.")
    return render(request, 'home.html')

def unit(request):  
    return render(request, 'unit.html')



def creacc(request):
    if request.method == 'POST':
        form = Tenantform(request.POST)
        if form.is_valid():
            tent_name = form.cleaned_data['tent_name']
            uname = form.cleaned_data['tent_uname']
            unit_type = form.cleaned_data['unit_type']
            tent_pnum = form.cleaned_data['tent_pnum']
            tent_emel = form.cleaned_data['tent_emel']
            tent_pword = form.cleaned_data['tent_pword']

            try:
                tenant = Tenants.objects.create(
                    tent_name=tent_name,
                    username=uname,
                    unit_type=unit_type,
                    tent_pnum=tent_pnum,
                    tent_emel=tent_emel,
                    password=tent_pword
                )
            
                subject = 'Account Creation'
                message = f'''
                            Your Account Information are the following:
                            - Username: {uname}
                            - Password: {tent_pword}
                        '''
                from_email = 'renafjunior@gmail.com'
                recipient_list = [ tent_emel]
                send_mail(subject, message, from_email, recipient_list)

                messages.success(request, "Account Created.")
                return redirect('creacc')  # Redirect after successful submission
            except IntegrityError as e:
                messages.error(request, f"Error creating account: {e}")
        else:
            messages.error(request, "Form is not valid. Please check the form data.")
    else:
        form = Tenantform()
    return render(request, 'creacc.html', {'form': form})

def ad_hom(request):
    book = Booked.objects.filter(approval_status='pending').order_by('date')
    tent = Tenants.objects.all().order_by('tent_name')
    prop = Units.objects.all()

    total_profit = calculate_total_profit()
    if total_profit is not None:
        formatted_total_profit = locale.currency(total_profit, grouping=True)
    else:
        formatted_total_profit = '0'  # or any default value you want to set

    num_tenants = tent.count()
    num_unit = prop.count()

    reqs = {
        'total_profit': formatted_total_profit,
        'Booked': book,
        'Tenants': tent,
        'Prop': prop,
        'NumTenants': num_tenants,
        'NumUnits': num_unit
    }
    return render(request, 'ad_hom.html', reqs)

def calculate_total_profit():
    try:
        total_profit = Payment.objects.aggregate(Sum('amount'))['amount__sum']
        if total_profit is not None:
            total_profit = abs(total_profit)
        return total_profit
    except Exception as e:
        # Log the exception for debugging
        print(f"Error in calculate_total_profit: {e}")
        return None





def ad_tent(request):
    # Query the Tenants model to get all tenants
    queryset = Tenants.objects.all()

    # Check if it's an AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Serialize the queryset to JSON data and return JSON response
        tenants_data = serialize('json', queryset)
        parsed_data = json.loads(tenants_data)
        return JsonResponse(parsed_data, safe=False)

    # If it's a regular GET request, render the HTML template
    return render(request, 'ad_tent.html', {'Tenants': queryset})

def homepage(request):      
    return render(request, 'homepage.html')

def contact(request):  
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        unit_type = request.POST.get('unit')
        comment = request.POST.get('comment')
        move_in_date = request.POST.get('date')

        subject = 'New Contact Form Submission'
        message = f'Name: {name}\nEmail: {email}\nPhone: {phone}\nUnit Type: {unit_type}\nComment: {comment}\nMove-in Date: {move_in_date}'
        from_email = settings.EMAIL_HOST_USER 
        recipient_list = ['renafjunior@gmail.com']

        send_mail(subject, message, from_email, recipient_list)

        return HttpResponse('Form submitted successfully. Thank you!')
    return render(request, 'contact.html')

def vtour(request):  
    return render(request, 'vtour.html')

def amnts(request):  
    return render(request, 'amnts.html')

def book(request):  
    if request.method == 'POST':
        form = Requestform(request.POST)
        if form.is_valid():
            nem = form.cleaned_data['name']
            emel= form.cleaned_data['emel']
            unit = form.cleaned_data['unit']
            pnum = form.cleaned_data['pnum']
            date = form.cleaned_data['date']
            bookt = form.cleaned_data['bookt']
            image = form.cleaned_data['image']
            try:
                book = Booked.objects.create(
                    name = nem,
                    emel = emel,
                    unit= unit,
                    pnum = pnum,
                    date = date,
                    bookt = bookt,
                    image = image
                )
                messages.success(request,'''Booking Submitted
                Thank you for submitting your booking. 
                                 Please wait for confirmation. ''')
            except IntegrityError:
                messages.error(request, "Invalid Input.")
    else:
        form = Requestform()
    return render(request, 'booking.html', {'form': form})

def comp(request):  
    comp = Issues.objects.all()
    payment = Payment.objects.filter(status='Pending').order_by('date')
    context = {
        'comp': comp,
        'pay': payment
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        custom_id_value = request.POST.get('custom_id')
        if action == 'approve':
            payment = Payment.objects.get(pk=custom_id_value)
            payment.status = 'Successful'
            payment.save()

        elif action == 'decline':
            payment = Payment.objects.get(pk=custom_id_value)
            payment.status = 'Decline'
            payment.save()

            messages.error(request, "Invalid Input.")

    return render(request, 'comp.html' ,{ **context })


def req(request):  
    book = Booked.objects.filter(approval_status='Pending').order_by('date')
    reqy = {
        'Booked': book
    }
    if request.method == 'POST':
        action = request.POST.get('action')
        custom_id_value = request.POST.get('custom_id')
        emel = request.POST.get('emel')
        if action == 'approve':
            booking = Booked.objects.get(pk=custom_id_value)
            booking.approval_status = 'approved'
            booking.save()

            subject = 'Booking Approved'
            message = ''' Your Booking is Approved
                        
                        To complete your payment, please use the following details:

                        Payment Method: Bank Transfer

                        Account Number: 001920196925
                        Account Holder: Rozaida Perio

                        Or you can make the payment via Gcash:

                        Gcash Number: 0917-533-0418
                        Account Holder: Rozaida Perio

                        Please ensure to include the unique transaction reference [XYZ123] when making the payment.

                        Thank you for choosing our services!
                      '''
            from_email = 'renafjunior@gmail.com'
            recipient_list = [emel]
            send_mail(subject, message, from_email, recipient_list)

        elif action == 'decline':
            booking = Booked.objects.get(pk=custom_id_value)
            booking.approval_status = 'declined'
            booking.save()

            subject = 'Booking Declined'
            message = 'Your booking has been declined.'
            from_email = 'renafjunior@gmail.com'
            recipient_list = [emel]
            send_mail(subject, message, from_email, recipient_list)

            messages.error(request, "Invalid Input.")

        
    return render(request, 'ad_req.html', reqy)


def nav(request):  
    return render(request, 'navbar.html')


def pay(request, username):
    try:
        tenant = Tenants.objects.get(username=username)
    except ObjectDoesNotExist:
        messages.error(request, "Tenant not found.")
        return redirect('book')

    context = {'username': username, 'tenant_id': tenant.id}
    
    if request.method == 'POST':
        form = Paymentform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            date = form.cleaned_data['date']
            unit = form.cleaned_data['unit']
            ref = form.cleaned_data['ref']
            mop = form.cleaned_data['mop']
            amount = form.cleaned_data['amount']
            tenant_id = form.cleaned_data['tenant']
            try:
                payment = Payment.objects.create(
                    name=name,
                    date=date,
                    unit=unit,
                    ref=ref,
                    mop=mop,
                    amount=amount,
                    tenant=tenant_id  
                                                    )
                messages.success(request, "Payment Submitted.")

            except IntegrityError:
                messages.error(request, "Invalid Input.")
        else:
            messages.error(request, "Invalid Form Data.")
    else:
        form = Paymentform()

    return render(request, 'payment.html', {'form': form, **context})

def prop(request):  
    queryset = Units.objects.all()
    context = {
        'Units': queryset
    }
    if request.method == 'POST':       
        form = Propform(request.POST)       
        if form.is_valid():
            untp = form.cleaned_data['unit_type']
            blt = form.cleaned_data['unit_blt'] 
            prc = form.cleaned_data['unt_price']

            try:
                units = Units.objects.create(
                    unit_type=untp,
                    unit_blt=blt,  
                    unt_price=prc
                )
                messages.success(request, "Unit Created.")
                return redirect('prop')  # Redirect to the property page after form submission
            except IntegrityError:
                messages.error(request, "Invalid Input.")
        else:
            messages.error(request, "Invalid Form Data.")
    else:
        form = Tenantform()

    return render(request, 'property.html', {'form': form, **context})

def rep(request):  
    if request.method == 'GET':
        try:
            start_year = int(request.GET.get('start_year', datetime.now().year))
            start_month = int(request.GET.get('start_month', datetime.now().month))
            end_year = int(request.GET.get('end_year', datetime.now().year))
            end_month = int(request.GET.get('end_month', datetime.now().month))

            # Validate input values
            if 1 <= start_month <= 12 and 1 <= end_month <= 12:
                _, last_day_start = monthrange(start_year, start_month)
                start_date = datetime(start_year, start_month, 1).date()
                _, last_day_end = monthrange(end_year, end_month)
                end_date = datetime(end_year, end_month, last_day_end).date()

                # Query the Payment model to get the total amount for the selected range of months
                total_amount = Payment.objects.filter(date__range=(start_date, end_date)).aggregate(Sum('amount'))['amount__sum']

                # Prepare data to pass to the template
                report_period = f'{start_date.strftime("%B %Y")} - {end_date.strftime("%B %Y")}'
                monthly_sums = {
                    report_period: total_amount or 0
                }

                # Get a list of years for the dropdown
                years = [start_year, end_year]  # You can customize this based on your data

                # Get a list of months for the dropdowns
                months = [(str(i), datetime(2000, i, 1).strftime('%B')) for i in range(1, 13)]

                return render(request, 'ad_rep.html', {
                    'monthly_sums': monthly_sums,
                    'start_year': start_year,
                    'start_month': start_month,
                    'end_year': end_year,
                    'end_month': end_month,
                    'report_period': report_period,
                    'years': years,
                    'months': months
                })
            else:
                return HttpResponse("Invalid month value. Please select a month between 1 and 12.")
        except ValueError:
            return HttpResponse("Invalid input. Please provide valid year and month values.")
    else:
        # Handle other HTTP methods if necessary
        pass


@login_required(login_url='home')  
def admins(request):  
    return render(request, 'admins.html')

@login_required(login_url='home') 
def tnt_hom(request):
    username = request.GET.get('username', '')

    try:
        tenant_data = Tenants.objects.get(username=username)
        tenant_name = tenant_data.tent_name
    except Tenants.DoesNotExist:
        tenant_name = None

    paypend = Payment.objects.filter(name=username, status='Pending')
    paypsucc = Payment.objects.filter(name=username, status='Successful')

    context = {
        'username': username,
        'tenant_name': tenant_name,
        'paypend': paypend,
        'paypsucc': paypsucc,
    }

    if request.method == 'POST':
        form = Compform(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            issue = form.cleaned_data['issue']
            solution = form.cleaned_data['solution']
            try:
                issue_obj = Issues.objects.create(name=name, issue=issue, solution=solution)
                messages.success(request, "Complaint submitted successfully.")
            except IntegrityError:
                messages.error(request, "Invalid Input.")
        else:
            messages.error(request, "Invalid Form Data.")
    else:
        form = Compform()

    context['form'] = form  # Add the form to the context

    return render(request, 'tnt_hom.html', context)

def foot(request):  
    return render(request, 'footer.html')






