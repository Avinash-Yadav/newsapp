from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.contrib.auth import authenticate, login , logout
from .models import Course, Department, User, Student, ExamPaper, Material, Announcement, CourseAllotment, Bookmark
from .forms import RegisterForm , LoginForm , AnnouncementForm , MaterialForm , ExamPaperForm
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm , LoginForm
from django.core import serializers
from django.http import JsonResponse,HttpResponse
from django.urls import reverse
import datetime
import json
# Create your views here.
def home(request):
    print(request.user)
    bookmarks  =Bookmark.objects.filter(user=request.user)
    bookmarkcourses = Bookmark.objects.select_related('course').filter(user=request.user)
    courselist=[]
    for bookmark in bookmarks:
        courselist.append(bookmark.course)
    start_from = int(request.GET.get('start_from',0))
    announcements = Announcement.objects.select_related('author').filter(course__in=courselist).order_by('-updated_on')[start_from*3:start_from*3+3]
    print(bookmarkcourses[0].course.name)
    return render(request,"feed.html",context={"feed":announcements,"next":start_from+1,"bookmark":bookmarkcourses})

def about(request):
    return render(request,"about.html",context={'':""})

def _logout(request):
    logout(request)
    return redirect('home')

def _login(request):
    if request.method =='GET':
        form = LoginForm()
        return render(request,"login.html",context={"form":form})
    elif request.method == 'POST':
        email    = request.POST.get('email')
        password = request.POST.get('password')
        user     = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                print(user.email)
                return redirect('home')
        print("no success")
        return redirect('home')
        

def _register(request,register_as=None):
    if request.method =='GET':
        form = RegisterForm()
        return render(request,"register.html",context={"form":form})  
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if(register_as=='student'):
                user.user_role = 'student'
            elif(register_as=='instructor'):
                user.user_role = 'instructor'
            user.save()
            return redirect(reverse('login'))
        return redirect(reverse('register',kwargs={"register_as":register_as}))
            

def profile(request):
    if request.method == 'GET':
        if request.user.user_role == "student":
            student,created = Student.objects.get_or_create(user=request.user)
            return render(request,"profile.html",context={"user":request.user,"student":student})
    elif request.method =='POST':
        pass 
        # Profile edit to be implemented.

def getDepartments(request):
    if request.method =='GET':
        dept = serializers.serialize("json",Department.objects.all(),use_natural_foreign_keys=True)
        data = json.loads(dept)
        result = {"result":data}
        return HttpResponse(json.dumps(result),content_type='application/json')


def getCourses(request,department=None):
    if request.method =='GET':
        dept   = get_object_or_404(Department,acronym=department)
        course = serializers.serialize("json",Course.objects.filter(dept=dept),use_natural_foreign_keys=True)
        data = json.loads(course)
        result = {"result":data}
        return HttpResponse(json.dumps(result),content_type='application/json')

@login_required
def Announcements(request,department=None,coursecode=None):
    if request.method =='GET':
        form= AnnouncementForm()
        return render(request,"form.html",context={"form":form})
    elif request.method =="POST":
        form = AnnouncementForm(request.POST,request.FILES)
        if(form.is_valid()):
            obj=Announcement()
            obj.files = form.cleaned_data["files"]
            obj.title = form.cleaned_data["title"]
            obj.description = form.cleaned_data["description"]
            obj.author=request.user
            obj.course= Course.objects.get(code=coursecode)
            obj.save()
            return redirect(reverse("course", kwargs={'department':department,'coursecode':coursecode}))
        print(form.errors) 
        return redirect(reverse("course", kwargs={'department':department,'coursecode':coursecode}))

@login_required
def Materials(request,department=None,coursecode=None):
    if request.method =='GET':
        form= MaterialForm()
        return render(request,"form.html",context={"form":form})
    elif request.method =="POST":
        form = MaterialForm(request.POST,request.FILES)
        if(form.is_valid()):
            obj = Material()
            obj.files = form.cleaned_data["files"]
            obj.title = form.cleaned_data["title"]
            obj.author=request.user
            obj.course= Course.objects.get(code=coursecode)
            obj.save()
            return redirect(reverse("course", kwargs={'department':department,'coursecode':coursecode}))
        print(form.errors) 
        return redirect(reverse("course", kwargs={'department':department,'coursecode':coursecode}))

@login_required
def ExamPaperView(request,department=None,coursecode=None):
    if request.method =='GET':
        form= ExamPaperForm()
        return render(request,"form.html",context={"form":form})
    elif request.method =="POST":
        form = ExamPaperForm(request.POST,request.FILES)
        if(form.is_valid()):
            obj = ExamPaper()
            obj.files = form.cleaned_data["files"]
            obj.term = form.cleaned_data["term"]
            obj.author=request.user
            obj.course= Course.objects.get(code=coursecode)
            obj.save()
            return redirect(reverse("course", kwargs={'department':department,'coursecode':coursecode}))
        print(form.errors) 
        return redirect(reverse("course", kwargs={'department':department,'coursecode':coursecode}))

@login_required
def DepartmentView(request,department=None):
    if request.method =='GET':
        dept    = get_object_or_404(Department,acronym=department)
        # courses = Course.objects.filter(dept=dept)
        # courseallotment = CourseAllotment.objects.filter(course__in=courses)
        # li_courses =[]
        # for course in courses:
        #     dict_courses =dict()
        #     dict_courses["name"]     = course.name
        #     dict_courses["code"]     = course.code
        #     try:
        #         dict_courses["semester"] = CourseAllotment.objects.get(course=course).semester
        #     except:
        #         dict_courses["semester"] = 0
        #     dict_courses["year"]     = (dict_courses["semester"]+1)//2
        #     li_courses.append(dict_courses)

        course = CourseAllotment.objects.select_related('course').filter(course__dept=dept).order_by('semester')
        return render(request,"department.html",context={"department":dept,"courses":course})

@login_required
def CourseView(request,department=None,coursecode=None):
    if request.method =='GET':
        dept          = get_object_or_404(Department,acronym=department)
        course        = get_object_or_404(Course,code=coursecode)
        announcements = Announcement.objects.filter(course=course)
        materials     = Material.objects.filter(course=course)
        papers        = ExamPaper.objects.filter(course=course)
        try:
            bookmark  = Bookmark.objects.get(course=course,user=request.user)
        except:
            bookmark  = None
        is_bookmarked = True if bookmark else False   
        return render(request,"course.html",context={"department":dept,"course":course,"announcements":announcements,"materials":materials,"papers":papers,"is_bookmarked":is_bookmarked})
        
@login_required
def FeedView(request):
    if request.method=='GET':
        start_from = int(request.GET.get('start_from',0))
        announcements = Announcement.objects.select_related('author').all().order_by('-updated_on')[start_from*3:start_from*3+3]
        return render(request,"feed.html",context={"feed":announcements,"next":start_from+1})

@login_required
def BookmarkView(request):
    if request.method =='POST':
        course     = request.POST.get('course')
        user       = request.POST.get('user')
        course_obj = get_object_or_404(Course,id=course)
        try:
            bookmark  = Bookmark.objects.get(course=course,user=request.user)
        except:
            bookmark  = None
        if bookmark is not None:
            print("It was working")
            bookmark.delete()
        else:
            obj        = Bookmark()
            obj.course = course_obj
            obj.user   = request.user
            obj.save()
        return HttpResponse(json.dumps({"success":True}),content_type='application/json')

