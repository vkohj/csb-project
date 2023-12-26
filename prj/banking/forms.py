from django import forms

class ModifyPassword(forms.Form):
    password = forms.CharField(label="Password")
    password_confirm = forms.CharField(label="Confirm Password")

class ModifyBalance(forms.Form):
    balance = forms.IntegerField(label="Balance")
