from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect,Http404
from django.core.urlresolvers import reverse
from django import forms
from .models import User,Article
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

class LogForm(forms.Form): 
    name = forms.CharField(label='用户名',max_length=50)
    password = forms.CharField(label='密码',widget=forms.PasswordInput())

class RegForm(forms.Form): 
    name = forms.CharField(label='用户名',max_length=50)
    password = forms.CharField(label='密 码',widget=forms.PasswordInput())
    repeat = forms.CharField(label='确认密码',widget=forms.PasswordInput())

class ArticleForm(forms.Form): 
    title = forms.CharField(label='标题',max_length=100)
    body = forms.CharField(label='内容',widget=forms.Textarea)

# Create your views here.
def index(req):
	if not req.session.get('id'):
		return HttpResponseRedirect(reverse('login'))
	articles=Article.objects.order_by('-time')
	paginator=Paginator(articles,3)
	page=req.GET.get('page')
	try:
		contacts=paginator.page(page)
	except (EmptyPage,PageNotAnInteger):
		contacts=paginator.page(1)
	return render(req,'blog/index.html',{'userId':req.session.get('id'),'articles':contacts})

def regist(req):
	if req.session.get('id'):
		return HttpResponseRedirect(reverse('index'))
	if req.method=='POST':
		regForm=RegForm(req.POST)
		if regForm.is_valid():
			name=regForm.cleaned_data['name']
			password=regForm.cleaned_data['password']
			repeat=regForm.cleaned_data['repeat']
			if password==repeat:
				haven=User.objects.filter(name__exact=name)
				if haven:
					return render(req,'blog/result.html',{'msg':'账号已存在！'})
				else:
					User.objects.create(name=name,password=make_password(password))
					return render(req,'blog/result.html',{'msg':'ok','name':name})
			return render(req,'blog/result.html',{'msg':'密码不一致！'})
	return render(req,'blog/regist.html',{'regForm':RegForm()})

def login(req):
	if req.session.get('id'):
		return HttpResponseRedirect(reverse('index'))
	if req.method=='POST':
		logForm=LogForm(req.POST)
		if logForm.is_valid():
			name=logForm.cleaned_data['name']
			password=logForm.cleaned_data['password']
			user=User.objects.filter(name__exact=name)
			if user and check_password(password,user[0].password):
				req.session['id']=user[0].pk
				return HttpResponseRedirect(reverse('index'))
			return render(req,'blog/login.html',{'logForm':LogForm(),'msg':'账号或密码错误！'})
	return render(req,'blog/login.html',{'logForm':LogForm()})

def logout(req):
	if req.session.get('id'):
		del req.session['id']
	return HttpResponseRedirect(reverse('login'))

def newarticle(req):
	if req.session.get('id'):
		user=User.objects.get(pk=req.session.get('id'))
		if req.method=='POST':
			articleForm=ArticleForm(req.POST)
			if articleForm.is_valid():
				title=articleForm.cleaned_data['title']
				body=articleForm.cleaned_data['body']
				Article.objects.create(title=title,body=body,author=user)
				return HttpResponseRedirect(reverse('index'))
		return render(req,'blog/newarticle.html',{'articleForm':ArticleForm()})
	return HttpResponseRedirect(reverse('login'))

def article(req,articleId):
	user=req.session.get('id','anyone')
	try:
		article=Article.objects.get(pk=articleId)
	except Article.DoesNotExist:
		raise Http404('文章不存在')
	author=article.author.pk
	return render(req,'blog/article.html',{'article':article,'editable':user==author})

def editarticle(req,articleId):
	user=req.session.get('id','anyone')
	try:
		article=Article.objects.get(pk=articleId)
	except Article.DoesNotExist:
		raise Http404('文章不存在')
	author=article.author.pk
	if user!=author:
		return HttpResponseRedirect(reverse('article',args=[articleId]))
	user=User.objects.get(pk=user)
	if req.method=='POST':
		articleForm=ArticleForm(req.POST)
		if articleForm.is_valid():
			article.title=articleForm.cleaned_data['title']
			article.body=articleForm.cleaned_data['body']
			article.save()
			return HttpResponseRedirect(reverse('article',args=[articleId]))
	articleForm=ArticleForm(initial={'title':article.title,'body':article.body})
	return render(req,'blog/newarticle.html',{'articleForm':articleForm})

def delarticle(req,articleId):
	user=req.session.get('id','anyone')
	try:
		article=Article.objects.get(pk=articleId)
	except Article.DoesNotExist:
		raise Http404('文章不存在')
	if user!=article.author.pk:
		return HttpResponseRedirect(reverse('article',args=[articleId]))
	article.delete()
	return HttpResponse('done')

def user(req,hostId):
	userId=req.session.get('id','anyone')
	user=User.objects.get(pk=userId)
	try:
		host=User.objects.get(pk=hostId)
	except User.DoesNotExist:
		raise Http404('用户不存在')
	articles=host.articles.order_by('-time')
	paginator=Paginator(articles,3)
	page=req.GET.get('page')
	try:
		contacts=paginator.page(page)
	except (EmptyPage,PageNotAnInteger):
		contacts=paginator.page(1)
	followed=user in host.follower.all()
	followyou=user in host.follow.all()
	editable=str(userId)==hostId
	category=editable*4+followed*2+followyou
	return render(req,'blog/user.html',{'articles':contacts,'host':host,'category':category})

def follow(req,hostId):
	if not req.session.get('id'):
		return HttpResponseRedirect(reverse('login'))
	user=User.objects.get(pk=req.session.get('id'))
	try:
		host=User.objects.get(pk=hostId)
	except User.DoesNotExist:
		raise Http404('用户不存在')
	user.follow.add(host)
	return HttpResponse('done')

def cancelfollow(req,hostId):
	if not req.session.get('id'):
		return HttpResponseRedirect(reverse('login'))
	user=User.objects.get(pk=req.session.get('id'))
	try:
		host=User.objects.get(pk=hostId)
	except User.DoesNotExist:
		raise Http404('用户不存在')
	user.follow.remove(host)
	return HttpResponse('done')

def showfollow(req,hostId,boo):
	try:
		host=User.objects.get(pk=hostId)
	except User.DoesNotExist:
		raise Http404('用户不存在')
	boo=int(boo)
	if boo:
		follows=host.follow.all()
	else:
		follows=host.follower.all()
	paginator=Paginator(follows,3)
	page=req.GET.get('page')
	try:
		contacts=paginator.page(page)
	except (EmptyPage,PageNotAnInteger):
		contacts=paginator.page(1)
	return render(req,'blog/showfollow.html',{'follows':contacts,'name':host.name,'boo':boo})

def timeline(req):
	if not req.session.get('id'):
		return HttpResponseRedirect(reverse('login'))
	user=User.objects.get(pk=req.session.get('id'))
	articles=Article.objects.filter(author__in=user.follow.all()).order_by('-time')
	paginator=Paginator(articles,3)
	page=req.GET.get('page')
	try:
		contacts=paginator.page(page)
	except (EmptyPage,PageNotAnInteger):
		contacts=paginator.page(1)
	return render(req,'blog/timeline.html',{'articles':contacts})