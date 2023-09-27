from django import forms
from .models import goods as Post, User
from django.contrib.auth.hashers import check_password

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '아이디를 입력해주세요', 'class': 'login-input'}),
        label='아이디',
        label_suffix='', 
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '비밀번호를 입력해주세요', 'class': 'login-input'}),
        label='비밀번호',
        label_suffix='', 
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if password and username :
            try:
                user = User.objects.get(username = username)
            except User.DoesNotExist:
                self.add_error("username", "존재하지 않는 아이디입니다.")
                return

            if not check_password(password, user.password):
                self.add_error("password", "올바른 비밀번호를 입력해주세요.")
            else:
                self.user_id = user.id

class CustomRegistrationForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': '아이디를 입력해주세요', 'class': 'login-input'}),
        label='아이디',
        label_suffix='', 
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '비밀번호를 입력해주세요', 'class': 'login-input'}),
        label='비밀번호',
        label_suffix='', 
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': '비밀번호를 다시 입력해주세요', 'class': 'login-input'}),
        label='비밀번호 확인',
        label_suffix='', 
    )

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'price', 'description', 'location', 'images']