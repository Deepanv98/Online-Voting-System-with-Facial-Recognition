from django import forms
from .models import Candidate

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['candidate_id', 'full_name', 'party_name', 'party_symbol', 'bio']
