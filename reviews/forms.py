from django import forms
from reviews.models import Review
from catalog.models import Pet, PetBreed

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(5, '★★★★★ (5 Stars - Exceptional)'),
                 (4, '★★★★☆ (4 Stars - Great)'),
                 (3, '★★★☆☆ (3 Stars - Average)'),
                 (2, '★★☆☆☆ (2 Stars - Fair)'),
                 (1, '★☆☆☆☆ (1 Star - Poor)')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'comment', 'adopter_location', 'pet', 'breed']
        widgets = {
            'headline': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. In love with our sweet Maltipoo!'}),
            'comment': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Share your experience with our placement atelier, chaperoned transport, and puppy health...'}),
            'adopter_location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'City, State (e.g. Manhattan, NY)'}),
            'pet': forms.Select(attrs={'class': 'form-select'}),
            'breed': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['pet'].required = False
        self.fields['breed'].required = False
        self.fields['pet'].empty_label = 'Select Specific Puppy (Optional)'
        self.fields['breed'].empty_label = 'Select Breed (Optional)'
