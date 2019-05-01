from django.shortcuts import render, redirect, HttpResponse
from repository.models import UserInfo,BlogInfo
from web.Forms.Account import AccountInfoForm,LoginForm
from django.urls import reverse
def register(request):
    # 注册用户
    if request.method == 'GET':
        obj = AccountInfoForm(request)
        return render(request, "Account/register.html", {"obj": obj})
    else:
        obj = AccountInfoForm(request,request.POST)
        if obj.is_valid():
            del obj.cleaned_data["confirmPwd"]
            del obj.cleaned_data["checkCode"]
            # 我不知道这个数据值什么时候丢的，
            # obj.cleaned_data["email"]=request.POST.get("email") #发现是clean_XX方法没有了写返回值
            UserInfo.objects.create(**obj.cleaned_data)
            return redirect('/')
        else:
            return render(request, "Account/register.html", {"obj": obj})

def login(request):
    #登陆用户
    if request.method == 'GET':
        obj = LoginForm(request)
        return render(request, "Account/login.html", {"obj": obj})
    else:
        obj = LoginForm(request, request.POST)
        if obj.is_valid():
            del obj.cleaned_data["checkCode"]
            if(obj.cleaned_data["rbm"]) :
                request.session.set_expiry(60 * 60 * 24 * 7)
            # 通过用户信息 获取博客信息 ，进一步拿到博客的后缀名，跳转到个人主页
            # UserInfo（UserID）==》BlogInfo（surfix）
            userInfo=UserInfo.objects.filter(username=obj.cleaned_data["username"]).select_related("bloginfo").first()
            if userInfo.bloginfo.surfix:
                base_url = '/'
                base_url = reverse('home', kwargs={'site':userInfo.bloginfo.surfix})
                return redirect(base_url)
            else:
                return redirect('/')
        else:
            return render(request, "Account/login.html", {"obj": obj})

def logout(request):
    request.session['user_info'] = None
    return redirect('/')


