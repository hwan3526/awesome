from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class user(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    profile_img = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=11)
    activated = models.BooleanField()
    rating_score = models.DecimalField(max_digits=3, decimal_places=1)
    created_at = models.DateTimeField(auto_now_add=True)

class follow_User(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

class block_User(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocking_users')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked_by_user')
    created_at = models.DateTimeField(auto_now_add=True)

class evaluation_items(models.Model):
    score = models.DecimalField(max_digits=3, decimal_places=1)
    text = models.CharField(max_length=20)

class categories(models.Model):
    name = models.CharField(max_length=20)
    
class files(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
class sido_areas(models.Model):
    adm_code = models.CharField(max_length=2)
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=20)
    
class sigg_areas(models.Model):
    sido_area = models.ForeignKey(sido_areas,on_delete=models.CASCADE)
    adm_code = models.CharField(max_length=5)
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=20)

# class emd_areas(models.Model):
#     sigg_area =models.ForeignKey(sigg_areas, on_delete=models.CASCADE)
#     adm_code = models.CharField(max_length=10)
#     name = models.CharField(max_length=50)
#     geom = models.MultiPolygonField(srid=4326)
#     location = models.PointField(srid=4326)
#     version = models.CharField(max_length=20)

# class activity_areas(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     reference_area_id = models.IntegerField()
#     distance_meters = models.SmallIntegerField()
#     emd_area = ArrayField(models.ForeignKey(emd_areas, on_delete=models.CASCADE))
#     authenticated_at = models.DateTimeField(null=True)

class goods(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    selling_area = models.ForeignKey(sido_areas, on_delete=models.CASCADE)
    category = models.ForeignKey(categories, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    status = models.CharField(max_length=10)
    sell_price = models.IntegerField(null=True)
    view_price = models.IntegerField()
    description = models.TextField()
    refreshed_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

class goods_images(models.Model):
    goods = models.ForeignKey(goods, on_delete=models.CASCADE)
    file = models.ForeignKey(files, on_delete=models.CASCADE)

class transaction_reviews(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ForeignKey(goods, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    # evaluation_items = ArrayField(models.ForeignKey(evaluation_items, on_delete=models.CASCADE))
    evaluation_items_ids = models.ManyToManyField(evaluation_items)
    created_at = models.DateTimeField(auto_now_add=True)

class price_offers(models.Model):
    offerer = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ForeignKey(goods, on_delete=models.CASCADE)
    offered_price = models.IntegerField()
    accept_or_not = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class notifications(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ForeignKey(goods, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class notification_keywords(models.Model):
    register = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

class wish_lists(models.Model):
    register = models.ForeignKey(User, on_delete=models.CASCADE)
    goods = models.ForeignKey(goods, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class chat_room(models.Model):
    goods = models.ForeignKey(goods, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class chat_messages(models.Model):  
    chat_room = models.ForeignKey(chat_room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    message = models.CharField(max_length=500)
    read_or_not = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    title = models.CharField(max_length=200)
    price = models.IntegerField()
    description = models.TextField()
    location = models.CharField(max_length=100)
    images = models.ImageField(upload_to='post_images/') 
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, to_field='username')
    created_at = models.DateTimeField(auto_now_add=True, null=True) 

    product_reserved = models.CharField(max_length=1, default='N')  # 예약 여부
    product_sold = models.CharField(max_length=1, default='N')  # 판매 여부

    view_num = models.PositiveIntegerField(default=0)  # 조회 수
    chat_num = models.PositiveIntegerField(default=0)  # 채팅 수

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    region = models.CharField(max_length=100, null=True)
    region_certification = models.CharField(max_length=1, default='N')

    def __str__(self):
        return f'{self.user.username} Profile'
    