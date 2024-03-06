from django.db import models
from django.utils import timezone

class User(models.Model):
    cin = models.CharField(max_length=128 ,unique=True)
    phone_number = models.IntegerField(default=0000000)
    date_de_delivrance = models.DateField(blank=True, default=timezone.now)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    statut = models.CharField(max_length=150, null=True)
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='last login')
    is_superuser = models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')
    first_name = models.CharField(blank=True, max_length=150, verbose_name='first name')
    last_name = models.CharField(blank=True, max_length=150, verbose_name='last name')
    is_active = models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')
    reset_password = models.BooleanField(default=False, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')

    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    def put(self, *args, **kwargs):
        if self.pk:
            # Créer une nouvelle instance avec les mêmes données
            new_version = User.objects.create(
                cin=self.cin,
                phone_number=self.phone_number,
                date_de_delivrance=self.date_de_delivrance,
                email=self.email,
                password=self.password,
                statut=self.statut,
                last_login=self.last_login,
                is_superuser=self.is_superuser,
                first_name=self.first_name,
                last_name=self.last_name,
                is_active=self.is_active,
                reset_password=self.reset_password,
                previous_version=self  # Référence vers la version précédente
            )
            # Mettre à jour la référence de la version précédente de l'instance actuelle
            self.previous_version = new_version
            # Enregistrer l'instance actuelle avec la nouvelle référence
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)
