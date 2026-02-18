from django.db import models

# Create your models here.
class Wallet(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    public_key = models.CharField(max_length=56)
    # Increased length to accommodate encrypted secret seed
    secret_seed = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + self.public_key