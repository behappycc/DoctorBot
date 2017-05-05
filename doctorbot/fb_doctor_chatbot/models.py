from django.db import models

# Create your models here.
class fb_db(models.Model):
	content = models.TextField()
	time = models.DateTimeField(auto_now_add = True)

	def publish(self):
		self.published_date = timezone.now()
		self.save()
	def __str__(self):
		return self.title
