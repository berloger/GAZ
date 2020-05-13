from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import (
    LoginForm,
    RegisterForm,
    ContractForm,
    SumsBYNForm,
    SumsRURForm,
)
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.views import View
from datetime import date
from .models import (
    Contract,
    SumsBYN,
    SumsRUR,
)
from django.forms import model_to_dict


@login_required
def index(request):
    return render(request, 'planes/index.html')


@login_required
def logout_view(request):
    logout(request)
    return render(request, 'planes/index.html')


def login_view(request,):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/')
                else:
                    return HttpResponse('disable account')
            else:
                return redirect('/login/')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def register_view(request):
    form = None
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        email = request.POST.get('email')
        username = request.POST.get('username')
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким адресом уже существует')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
        else:
            if form.is_valid():
                username = form.cleaned_data['username']
                email = email
                password = User.objects.make_random_password(4)
                user = User.objects.create_user(
                    username,
                    email,
                    password
                )
                user.save()
                send_mail(
                    'Hello from GAZ',
                    'Ваш пароль: ' + str(password),
                    'gazprombelgaz@gmail.com',
                    [email],
                    fail_silently=False
                )
                return HttpResponse(("Регистрация прошла успешна, пароль отправлен на почту: %s") % str(email))
    else:
        form = RegisterForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)


class ContractView(View):
    template_name = 'contracts/contract_main.html'
    today_year = date.today().year

    def get(self, request):
        contracts = Contract.objects.filter(start_date__contains=self.today_year).order_by('-id')
        contract_and_sum = []
        for contract in contracts:
            sum_byn = SumsBYN.objects.get(contract=contract)
            sum_rur = SumsRUR.objects.get(contract=contract)
            contract_and_sum.append(
                {
                    'contract':contract,
                    'sum_byn':sum_byn,
                    'sum_rur':sum_rur,
                }
            )
        return render(request,
                      template_name=self.template_name,
                      context={'contracts':contracts,
                               'contract_and_sum':contract_and_sum,
                               })


@login_required()
def create_contract(request):
    if request.method == 'POST':
        contract_form = ContractForm(request.POST)
        sum_b_form = SumsBYNForm(request.POST)
        sum_r_form = SumsRURForm(request.POST)
        if \
                contract_form.is_valid() \
                and sum_b_form.is_valid() \
                and sum_r_form.is_valid():
            new_contract = contract_form.save()
            contract_sum_b = sum_b_form.save(commit=False)
            contract_sum_b.contract = new_contract
            contract_sum_b.save()
            contract_sum_r = sum_r_form.save(commit=False)
            contract_sum_r.contract = new_contract
            contract_sum_r.save()

    contract_form = ContractForm
    sum_b_form = SumsBYNForm
    sum_r_form = SumsRURForm
    return render(request,
                  template_name='contracts/add_new_contract.html',
                  context={
                      'contract_form':contract_form,
                      'sum_b_form':sum_b_form,
                      'sum_r_form':sum_r_form,
                  })


def change_contract(request, contract_id):
    if request.method == 'POST':
        contract = Contract.objects.get(id=contract_id)
        contract_sum_b = SumsBYN.objects.get(contract=contract)
        contract_sum_r = SumsRUR.objects.get(contract=contract)
        contract_form = ContractForm(request.POST, instance=contract)
        sum_b_form = SumsBYNForm(request.POST, instance=contract_sum_b)
        sum_r_form = SumsRURForm(request.POST, instance=contract_sum_r)
        if \
                contract_form.is_valid() \
                and sum_b_form.is_valid() \
                and sum_r_form.is_valid():
            new_contract = contract_form.save()
            contract_sum_b = sum_b_form.save(commit=False)
            contract_sum_b.contract = new_contract
            contract_sum_b.save()
            contract_sum_r = sum_r_form.save(commit=False)
            contract_sum_r.contract = new_contract
            contract_sum_r.save()



    contract_item = Contract.objects.get(id=contract_id)
    sum_byn_item = SumsBYN.objects.get(contract=contract_item)
    sum_rur_item = SumsRUR.objects.get(contract=contract_item)
    initial_contract = model_to_dict(contract_item)
    initial_sum_byn = model_to_dict(sum_byn_item)
    initial_sum_rur = model_to_dict(sum_rur_item)

    contract_form = ContractForm(instance=contract_item)
    sum_b_form = SumsBYNForm(instance=sum_byn_item)
    sum_r_form = SumsRURForm(instance=sum_rur_item)
    return render(request,
                  template_name='contracts/add_new_contract.html',
                  context={
                      'contract_form':contract_form,
                      'sum_b_form':sum_b_form,
                      'sum_r_form':sum_r_form,
                  })
