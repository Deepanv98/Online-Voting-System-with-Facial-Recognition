from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Candidate(models.Model):
    full_name = models.CharField(max_length=100)
    party_name = models.CharField(max_length=100)
    party_symbol = models.ImageField(upload_to='party_symbols/')
    bio = models.TextField()

    def __str__(self):
        return self.full_name


class VotingResult(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    cast_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Voter {self.voter.username} voted for {self.candidate.name} on {self.cast_at}"

