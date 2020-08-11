from django.db import models

# Create your models here.

class Profile(models.Model):
	external_id = models.PositiveIntegerField(
		verbose_name="Id пользователя социальной сети",
			unique=True,
	)

	def __str__(self):
		return f'#{self.external_id}'

	class Meta:
		verbose_name = "Профиль"
		verbose_name_plural = 'Профили'
