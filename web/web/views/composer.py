from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from web.helpers.code import gen_code, send_sms_code,verify
from web.models.code import Code
from web.models.composer import Composer
from web.helpers.composer import get_posts_by_cid


def oneuser(request, cid):
    composer = Composer.objects.get(cid=cid)
    composer.posts = get_posts_by_cid(cid, 2)
    return render(request, 'oneuser.html', locals())


def homepage(request, cid):
    composer = Composer.objects.get(cid=cid)
    composer.posts = get_posts_by_cid(cid)
    composer.rest_posts = composer.posts[1:]
    return render(request, 'homepage.html', locals())

def register(request):
    return render(request,'register.html')

def do_register(request):
    nickname = request.POST.get('nickname')
    phone = request.POST.get('phone')
    code = request.POST.get('code')
    password = request.POST.get('password')
    prefix_code = request.POST.get('prefix_code')
    callback = request.POST.get('callback')
    if Composer.objects.filter(phone=phone).exists():
        data =  {'status':-1025,'msg':'该手机号已注册过'}
        return JsonResponse(data)
    if not verify(phone,code):
        return JsonResponse({'status': -1,'msg': '手机验证失败'})

    composer = Composer()
    composer.cid = composer.phone = phone
    composer.name = nickname
    composer.password = password
    composer.avatar = ''
    composer.banner = ''
    composer.save()
    return JsonResponse({
        'status': 0,
        'data': {
            'callback': '/'
        }
    })


def login(request):
    return render(request,'login.html')

def do_login(request):
    phone = request.POST.get('value')
    password = request.POST.get('password')
    composer = Composer.get_by_phone(phone)
    if not composer or composer.password != password:
        return JsonResponse({'status': -1, 'msg': '用户名密码错误'})
    return JsonResponse({
        'status': 0,
        'data': {
            'callback': '/'
        }
    })

def send_code(request):
    prefix_code = request.POST.get('prefix_code')
    phone = request.POST.get('phone')
    composer = Composer.get_by_phone(phone)
    if composer:
        return JsonResponse({'status': -1025, 'msg': '该手机号已注册过'})
    code = Code()
    code.phone = phone
    code.code = gen_code()
    code.ip = request.META['REMOTE_ADDR']
    code.created_at = datetime.now()
    code.save()
    send_sms_code(phone, code.code)
    return JsonResponse({
        'status': 0,
        'msg': 'ok',
        'data': {
            'phone': phone,
            'prefix_code': prefix_code,
        }
    })