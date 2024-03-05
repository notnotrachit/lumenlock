from django.db import models

# Create your models here.
class Wallet(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    public_key = models.CharField(max_length=56)
    secret_seed = models.CharField(max_length=56)
    balance = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.public_key} - {self.balance}'

    def deposit(self, amount):
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if self.balance < amount:
            return False
        self.balance -= amount
        self.save()
        return True

    def transfer(self, amount, destination):
        if self.withdraw(amount):
            destination.deposit(amount)
            return True
        return False