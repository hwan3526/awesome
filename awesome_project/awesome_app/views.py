from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import goods as Post, user_profile as UserProfile, chat_room, chat_messages
from .forms import CustomRegistrationForm, CustomLoginForm, PostForm
from django.db.models import Q
from django.utils import timezone


def index(request):
    return render(request, 'awesome_app/main.html')

def register(request):
    error_message = ''

    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        username = request.POST.get('username')

        if User.objects.filter(username=username).exists():
            form.add_error('username', '이미 존재하는 아이디입니다. 다른 아이디를 입력해주세요.')
        elif form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                user = User.objects.create_user(username=username, password=password1)
                if user is not None:
                    login(request, user)
                    return redirect('awesome_app:login')
            else:
                form.add_error('password2', '비밀번호가 일치하지 않습니다.')
    else:
        form = CustomRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form, 'error_message': error_message})

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('awesome_app:main')
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
    # return render(request, 'awesome_app/trade_post.html', {'form': form})
    return redirect('awesome_app:trade')

def trade(request):
    top_views_posts = Post.objects.filter(product_sold='N').order_by('-view_num')

    for post in top_views_posts:
        chats = chat_room.objects.filter(goods=post, seller=post.user)
        post.chat_num = len(chats)
        post.save()

    return render(request, 'awesome_app/trade.html', {'posts': top_views_posts})

def find_room_number(request, post):
    room_number = 0
    find_room = chat_room.objects.filter(
        (Q(buyer=request.user.id) | Q(seller=request.user.id))
        &
        (Q(buyer=post.user.id) | Q(seller=post.user.id))
    ).first()

    if find_room:
        room_number = find_room.id

    return room_number

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

    room_number = find_room_number(request, post)

    context = {
        'post': post,
        'user_profile': user_profile,
        'room_number': room_number
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

def format_datetime(dt):
    today = timezone.now().date()
    if dt.date() == today:
        return dt.strftime("오늘 %p %I:%M")
    yesterday = today - timezone.timedelta(days=1)
    if dt.date() == yesterday:
        return dt.strftime("어제 %p %I:%M")
    return dt.strftime("%Y-%m-%d %p %I:%M")

def get_rooms(request):
    chat_rooms = chat_room.objects.filter(Q(buyer=request.user.id) | Q(seller=request.user.id))

    latest_messages = []
    for room in chat_rooms:
        try:
            unread_message_count = chat_messages.objects.filter(
                Q(chat_room=room),
                ~Q(sender=request.user),
                Q(read_or_not=False)
            ).count()

            latest_message = chat_messages.objects.filter(chat_room=room).latest('created_at')
            seller = None

            if latest_message.chat_room.buyer == request.user:
                seller = latest_message.chat_room.seller
            else:
                seller = latest_message.chat_room.buyer

            try:
                seller_location = UserProfile.objects.get(user=seller).region
            except UserProfile.DoesNotExist:
                seller_location = '' 

            latest_messages.append({
                'chat_room_id': room.id,
                'seller_id': seller.id,
                'seller': seller,
                'seller_location': seller_location,
                'message': latest_message.message,
                'created_at': format_datetime(latest_message.created_at),
                'unread_message_count': unread_message_count,
            })
        except chat_messages.DoesNotExist:
            seller = None

            if room.seller.id == request.user.id:
                seller = User.objects.get(pk=request.user.id)
            else:
                seller = room.seller

            try:
                seller_location = UserProfile.objects.get(user=seller).region
            except UserProfile.DoesNotExist:
                seller_location = '' 

            latest_messages.append({
                'chat_room_id': room.id,
                'seller_id': seller.id,
                'seller': seller.username,
                'seller_location': '',
                'message': '',
                'created_at': '',
                'unread_message_count': 0,
            })
            pass

    latest_messages.sort(key=lambda x: x['created_at'], reverse=True)

    return latest_messages

def get_recent_trade(seller_id):
    seller = User.objects.get(id=seller_id)
    goods = Post.objects.filter(user=seller).order_by('-created_at')

    return goods

def current_chat(request, room_number, seller_id):
    current_chat = None
    formatted_chat_msgs = []
    first_unread_index = -1

    if room_number == 0:
        if seller_id == request.user.id:
            # 네비바에서 '채팅하기' 클릭한 경우 고객상담챗 열리도록
            pass
        else:
            seller = User.objects.get(id=seller_id)
            buyer = User.objects.get(id=request.user.id)
            new_chat_room = chat_room.objects.create(buyer=buyer, seller=seller)
            room_number = new_chat_room.id
    else:
        current_room = chat_room.objects.get(id=room_number)
        current_chat = chat_messages.objects.filter(chat_room=current_room).order_by('created_at')     

        for i, chat in enumerate(current_chat):
            if chat.read_or_not == False:
                if chat.sender.id != request.user.id:
                    chat.read_or_not = True
                    chat.save()
                    if first_unread_index == -1:
                        first_unread_index = chat.id

        for chat in current_chat:
            formatted_chat_msgs.append({
                'created_at': format_datetime(chat.created_at),
                'message': chat.message,
                'username': chat.sender.username,
                'is_read': chat.read_or_not, 
                'id': chat.id,
            })

    seller_profile = {
        'username': '',
        'rating_score': 0.0
    }

    seller_profile['username'] = User.objects.get(id=seller_id).username

    try:
        profile = UserProfile.objects.get(id=seller_id)
        seller_profile['rating_score'] = profile.rating_score
    except UserProfile.DoesNotExist:
        pass

    context = {
        "room_number" : room_number,
        "chat_msgs" : formatted_chat_msgs,
        "latest_messages" : get_rooms(request),
        'first_unread_index': first_unread_index,
        'goods': get_recent_trade(seller_id),
        'seller': seller_profile
    }

    return render(request, 'awesome_app/chat.html', context)

@login_required
def chat_msg(request, room_number):
    room = get_object_or_404(chat_room, pk=room_number)

    current_time = timezone.now()
    three_days_ago = current_time - timezone.timedelta(days=3)
    chat_msgs = chat_messages.objects.filter(chat_room=room, created_at__gte=three_days_ago).order_by('-created_at')

    created_at = format_datetime(chat_msg.created_at)

    if request.method == 'POST':
        chatInput = request.POST.get('chat-send-msg')
        sender = request.user
        chat_msg = chat_messages(chat_room=room, sender=sender, message=chatInput, read_or_not=False)
        chat_msg.save()

        response_data = {
            'created_at': created_at,
            'message': chat_msg.message,
            'username': chat_msg.sender.username,
        }

        return JsonResponse(response_data)

    context = {
        "room_number" : room_number,
        "chat_msgs" : chat_msgs
    }

    return render(request, 'awesome_app/chat.html', context)

def location(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user.id)
        region = user_profile.region if user_profile.region != None else ''
    except UserProfile.DoesNotExist:
        obj = UserProfile(user=User.objects.get(id=request.user.id),activated=True,rating_score=0.0)
        obj.save()
        region = ''
    return render(request,'awesome_app/location.html',{"region": region})

def fix_location(request):
    user_profile = UserProfile.objects.get(user=request.user.id)
    region = user_profile.region
    return render(request,'awesome_app/fix_location.html',{"region": region})

def set_region(request):
    region = request.POST.get('region-setting')
    user_profile = UserProfile.objects.get(user=request.user.id)
    user_profile.region = region
    user_profile.region_certification = 'N'
    user_profile.save()
    return redirect('awesome_app:alert',alert_message='내 동네 설정이 완료되었습니다.')

def set_region_certification(request):
    user_profile = UserProfile.objects.get(user=request.user.id)
    user_profile.region_certification = 'Y'
    user_profile.save()
    return redirect('awesome_app:alert',alert_message='동네 인증이 완료되었습니다.')

# @login_required
# def chat(request, room_name, username):
#     users = User.objects.get(username=username)
#     # room_num = User.objects.get(room_name=room_name)
#     return render(request, 'awesome_app/chat.html', {'room_name': room_name, 'username':users})
