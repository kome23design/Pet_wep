from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import CustomerProfile, CustomerAddress

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Choose a secure password', 'class': 'form-input'})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone_number', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '(212) 555-0100', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'customer'
        if commit:
            user.save()
            CustomerProfile.objects.create(user=user)
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username or Email', 'class': 'form-input', 'autofocus': True})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-input'})
    )


class CustomerProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(max_length=25, required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = CustomerProfile
        fields = ['preferred_contact_method', 'residence_type', 'has_fenced_yard', 'has_experience_with_breed', 'newsletter_subscribed', 'special_care_notes']
        widgets = {
            'preferred_contact_method': forms.Select(attrs={'class': 'form-select'}),
            'residence_type': forms.Select(attrs={'class': 'form-select'}),
            'special_care_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': 'Any dietary or building access notes...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['phone_number'].initial = user.phone_number


class CustomerAddressForm(forms.ModelForm):
    class Meta:
        model = CustomerAddress
        fields = ['address_label', 'recipient_name', 'street_address', 'apartment_suite', 'city', 'state', 'postal_code', 'is_default', 'delivery_instructions']
        widgets = {
            'address_label': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Primary Manhattan Residence'}),
            'recipient_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'street_address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street Address'}),
            'apartment_suite': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apt, Suite, Penthouse'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'State (e.g. NY)'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ZIP Code'}),
            'delivery_instructions': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Doorman lobby instructions, elevator access...'}),
        }
