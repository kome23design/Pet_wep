from django import forms
from orders.models import Order
from datetime import date, timedelta

US_STATES = [
    ('', 'Select State'),
    ('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'),
    ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'),
    ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'),
    ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'),
    ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'),
    ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'),
    ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'),
    ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'),
    ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'),
    ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'),
    ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'),
    ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('DC', 'District of Columbia'),
]

DELIVERY_WINDOWS = [
    ('Morning (9:00 AM - 1:00 PM EST)', 'Morning (9:00 AM - 1:00 PM EST)'),
    ('Afternoon (1:00 PM - 5:00 PM EST)', 'Afternoon (1:00 PM - 5:00 PM EST)'),
    ('Evening (5:00 PM - 8:00 PM EST)', 'Evening (5:00 PM - 8:00 PM EST)'),
    ('Flexible / Coordinated by Atelier', 'Flexible / Coordinated by Atelier'),
]

class CheckoutForm(forms.ModelForm):
    delivery_state = forms.ChoiceField(choices=US_STATES, widget=forms.Select(attrs={'class': 'form-select'}))
    preferred_delivery_window = forms.ChoiceField(choices=DELIVERY_WINDOWS, widget=forms.Select(attrs={'class': 'form-select'}))
    preferred_delivery_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'min': (date.today() + timedelta(days=2)).isoformat()}),
        required=False,
        help_text='Delivery dates require 48 hours for pre-travel veterinary health inspection clearance.'
    )
    payment_choice = forms.ChoiceField(
        choices=(
            ('paypal', 'PayPal'),
            ('chime', 'Chime'),
            ('cashapp', 'Cash App'),
            ('apple_pay', 'Apple Pay'),
        ),
        widget=forms.RadioSelect,
        initial='paypal'
    )
    coupon_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter Promo Code (e.g. PRESTIGE10)'})
    )
    create_account = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox', 'id': 'create_account_toggle'}),
        help_text='Save my information and create a private client atelier account.'
    )
    account_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Create secure password (min. 8 characters)', 'id': 'account_password_input'})
    )
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        error_messages={'required': 'You must accept the Prestige Paws Placement Terms.'}
    )
    welfare_policy_acknowledged = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        error_messages={'required': 'You must acknowledge our Animal Welfare and Chaperoned Transport Policy.'}
    )

    class Meta:
        model = Order
        fields = [
            'customer_name', 'customer_email', 'customer_phone',
            'delivery_street_address', 'delivery_apartment', 'delivery_city',
            'delivery_state', 'delivery_postal_code', 'delivery_notes',
            'preferred_delivery_date', 'preferred_delivery_window',
            'customer_notes', 'terms_accepted', 'welfare_policy_acknowledged'
        ]
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@example.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '(212) 555-0199'}),
            'delivery_street_address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Street Address'}),
            'delivery_apartment': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Apartment, Suite, Unit'}),
            'delivery_city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City'}),
            'delivery_postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'ZIP Code'}),
            'delivery_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Building entry instructions, doorman notes, flight details...'}),
            'customer_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': 'Special preferences for your puppy settling in...'}),
        }

    def clean_delivery_postal_code(self):
        zip_code = self.cleaned_data.get('delivery_postal_code', '').strip()
        if len(zip_code) < 5:
            raise forms.ValidationError('Please enter a valid 5-digit US ZIP code.')
        return zip_code
