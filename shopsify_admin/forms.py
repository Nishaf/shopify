from django.core.validators import RegexValidator,EmailValidator
from django import forms
from .models import *


class UserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'username', 'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'first_name', 'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'last_name', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'size': 50, 'placeholder': 'password', 'class': 'form-control'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'email', 'class': 'form-control'}))
    image = forms.ImageField()
    group_name = forms.ModelChoiceField(queryset=UserGroups.objects.all(), required=False)
    customer = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'image', 'group_name']


class GroupForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'group_name', 'class': 'form-control'}))
    number_of_sites = forms.CharField(
        widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'XX', 'class': 'form-control'}))

    class Meta:
        model = UserGroups
        fields = ['name', 'number_of_sites']

class SettingsForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    proxy_api = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    update_period = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    class Meta:
        model = ShopifySettingsModel
        fields = ['name', 'proxy_api', 'update_period']


class AddSiteForm(forms.ModelForm):
    category = forms.CharField(widget=forms.HiddenInput, required=False)
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    url = forms.URLField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    total_products = forms.CharField(widget=forms.HiddenInput, required=False, initial=0)
    last_update_date = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = ShopifySiteModel
        fields = ['name', 'url', 'total_products', 'last_update_date']



class ProfileForm(forms.ModelForm):
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'first_name', 'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'last_name', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.HiddenInput(), required=False)
    email = forms.CharField(widget=forms.HiddenInput(), required=False)
    image = forms.ImageField()
    customer = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'image']


class PasswordForm(forms.ModelForm):
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    first_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    last_name = forms.CharField(widget=forms.HiddenInput(), required=False)
    password = forms.CharField(label='New Password',
                               widget=forms.PasswordInput(attrs={'size': 50,
                                                             'class': 'form-control'}))
    email = forms.CharField(widget=forms.HiddenInput(), required=False)
    image = forms.ImageField(widget=forms.HiddenInput(), required=False)
    customer = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = User
        fields = ['password']


class ProductExtractorForm(forms.Form):
    url = forms.URLField(max_length=200)
    download_info = forms.BooleanField(initial=True)
    download_images = forms.BooleanField(initial=True)



class EditUserForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'username',
                                                             'class': 'form-control', 'disabled': True}), required=False)
    first_name = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'first_name', 'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'last_name', 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'size': 50, 'placeholder': 'password', 'class': 'form-control'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'size': 50, 'placeholder': 'email', 'class': 'form-control'}))
    image = forms.ImageField()
    group_name = forms.ModelChoiceField(queryset=UserGroups.objects.all(), required=False)
    customer = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'image', 'group_name']
