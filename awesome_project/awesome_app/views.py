from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import goods as Post, user_profile as UserProfile
from .forms import CustomRegistrationForm, CustomLoginForm, PostForm
from django.db.models import Q


def index(request):
    return render(request, 'awesome_app/main.html')

def register(request):
    error_message = ''

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            error_message = "이미 존재하는 아이디입니다."
        elif form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                user = User.objects.create_user(username=username, password=password1)
                if user is not None:
                    login(request, user)
                    return redirect('awesome_app:login')
            else:
                form.add_error('password2', 'Passwords do not match')
    else:
        form = CustomRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form, 'error_message': error_message})

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        form = CustomLoginForm(data=request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('awesome_app:main')
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return render(request, "awesome_app/main.html")

def alert(request, alert_message):
    return render(request, 'awesome_app/alert.html', {'alert_message': alert_message})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)  # 임시 저장
            post.user = request.user  # 작성자 정보 추가 (이 부분을 수정했습니다)
            post.save()  # 최종 저장
            return redirect('awesome_app:trade_post', pk=post.pk)  # 저장 후 상세 페이지로 이동
    else:
        form = PostForm()
    return render(request, 'awesome_app/trade_post.html', {'form': form})

def trade(request):
    top_views_posts = Post.objects.filter(product_sold='N').order_by('-view_num')[:4] 
    print(top_views_posts)
    return render(request, 'awesome_app/trade.html', {'posts': top_views_posts})

# 중고거래상세정보(각 포스트) 화면
def trade_post(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user.is_authenticated:
        if request.user != post.user:
            post.view_num += 1
            post.save()
    else:
        post.view_num += 1
        post.save()

    try:
        user_profile = UserProfile.objects.get(user=post.user)
    except UserProfile.DoesNotExist:
            user_profile = None

    context = {
        'post': post,
        'user_profile': user_profile,
    }

    return render(request, 'awesome_app/trade_post.html', context)

@login_required
def write(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.region_certification == 'Y':
            return render(request, 'awesome_app/write.html')
        else:
            return redirect('awesome_app:alert', alert_message='동네인증이 필요합니다.')
    except UserProfile.DoesNotExist:
        return redirect('awesome_app:alert', alert_message='동네인증이 필요합니다.')
    
# 거래글수정 화면
def edit(request, id):
    post = get_object_or_404(Post, id=id)
    if post:
        post.description = post.description.strip()
    if request.method == "POST":
        post.title = request.POST['title']
        post.price = request.POST['price']
        post.description = request.POST['description']
        post.location = request.POST['location']
        if 'images' in request.FILES:
            post.images = request.FILES['images']
        post.save()
        return redirect('awesome_app:trade_post', pk=id)

    return render(request, 'awesome_app/write.html', {'post': post})


def search(request):
    query = request.GET.get('search')
    if query:
        results = Post.objects.filter(Q(title__icontains=query) | Q(location__icontains=query))
    else:
        results = Post.objects.all()
    
    return render(request, 'awesome_app/search.html', {'posts': results})

def location(request):
    return render(request, 'awesome_app/location.html')

def chat(request):
    region = ''
    return render(request, 'awesome_app/chat.html', {"region" : region})