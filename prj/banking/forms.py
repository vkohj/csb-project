from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=32)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class AdminLogin(forms.Form):
    key = forms.CharField(label="Key", widget=forms.PasswordInput)

class CreateUser(forms.Form):
    username = forms.CharField(label="Username", max_length=32)
    password = forms.CharField(label="Password")

class CreateAccount(forms.Form):
    num = forms.CharField(label="Account Number", max_length=15)
    balance = forms.IntegerField(label="Balance")

class ModifyPassword(forms.Form):
    password = forms.CharField(label="Password")
    password_confirm = forms.CharField(label="Confirm Password")

class ModifyBalance(forms.Form):
    balance = forms.IntegerField(label="Balance")

class SendForm(forms.Form):
    sender = forms.CharField(label="Sender", max_length=15, disabled=True)
    receiver = forms.CharField(label="Receiver", max_length=15)

    amount = forms.IntegerField(label="Amount")