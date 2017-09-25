from django.db import models
from django.contrib import admin

# Create your models here.
class User(models.Model):
	"""docstring for Post"""
	name = models.CharField(max_length=50,unique=True)
	password = models.CharField(max_length=255)
	follow = models.ManyToManyField('self',symmetrical=False,related_name='follower')
	def __str__(self):
		return self.name

class Article(models.Model):
	"""docstring for Post"""
	title = models.CharField(max_length=150)
	body = models.TextField()
	time = models.DateTimeField(auto_now=True)
	author =models.ForeignKey(User,related_name='articles',default=1)
	def __str__(self):
		return self.title

admin.site.register(User)
admin.site.register(Article)

