# -*- coding: utf-8 -*-

from django.utils.timezone import utc
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from shop.models import Item, Basket, Order, WriteComment, DeliveryDetail
from shop.shop_forms import CommentForm
from django.contrib.auth.models import User
from accounts.views import login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from operator import add

def get_cart(cur_basket):
    cart = []
    for (key, value) in cur_basket.iteritems():
        if key != 'sum' and key != 'count':
            basket = Basket(item_id=key, count=value)
            basket.sum = basket.item.price * basket.count
            cart.append(basket)
    return cart

def index(request):
    #if request.user:
    user = request.user
    choices = [('all', u'Любой тип')] + Item._meta.get_field('type').choices
    selected = 'all'
    if request.method == 'POST':
        type = request.POST.get('item_type')

        if type != 'all':
            selected = type
            item_list = Item.objects.filter(type=type).order_by()
        else:
            item_list = Item.objects.all()
    else:
        item_list = Item.objects.all().order_by('type')

    paginator = Paginator(item_list, 1) # Show 25 contacts per page

    page = request.GET.get('page')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)
    if 'basket' not in request.session:
        if not user.is_anonymous():
            order = Order(user_id=request.user.id, full_sum=0)
        else:
            order = Order(user_id=-1, full_sum=0)
        basket = {'sum': 0, 'count': 0}
        request.session['basket'] = basket


    context = {'items': items, 'user': user, 'choices': choices, 'selected': selected}
    return render(request, 'shop/index.html', context)


def add_to_basket(request, item_id):

    cur_basket = request.session['basket']
    basket = Basket(item_id=item_id, count=1)
    cur_basket['sum'] += basket.item.price
    cur_basket['count'] += 1
    if item_id not in cur_basket:
        cur_basket[item_id] = 1
    else:
        cur_basket[item_id] += 1
    request.session['basket'] = cur_basket
    return redirect('shop.views.index')

def product(request, item_id):

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.item_id = item_id
            if not request.user.is_anonymous():
                comment.user_id = request.user.id
            else:
                comment.user_id = -1
            comment.comment_date = datetime.now()
            comment.save()
    else:
        form = CommentForm()
    item = get_object_or_404(Item, pk=item_id)
    photos = item.get_photos()
    comments = item.get_comments()
    context = {'item': item, 'photos': photos, 'comments': comments, 'form': form}
    return render(request, 'shop/product.html', context)


def cart(request, item_id=0):
    user = request.user
    if 'basket' not in request.session:
        return redirect('shop.views.index')
    cur_basket = request.session['basket']

    cart = get_cart(cur_basket)
    #for (key, value) in cur_basket.iteritems():
    #    if key != 'sum' and key != 'count' and key != 'detail_id':
    #        basket = Basket(item_id=key, count=value)
    #        basket.sum = basket.item.price * basket.count
    #        cart.append(basket)
    if request.method == 'POST':
        return redirect('shop.views.make_order')

    #summary = reduce(add, [item.sum for item in forms])
    summary = cur_basket['sum']
    count = cur_basket['count']
    context = {'cart': cart, 'summary': summary, 'count': count}
    return render(request, 'shop/cart.html', context)

def add_count_in_basket(request, item_id):

    cur_basket = request.session['basket']
    basket = Basket(item_id=item_id, count=1)
    item = get_object_or_404(Item, pk=item_id)
    #if cur_basket[item_id] + 1 <= item.count:
    cur_basket['sum'] += basket.item.price
    cur_basket['count'] += 1
    cur_basket[item_id] += 1
    request.session['basket'] = cur_basket
    return redirect('shop.views.cart')

def remove_count_in_basket(request, item_id):

    cur_basket = request.session['basket']
    basket = Basket(item_id=item_id, count=1)
    item = get_object_or_404(Item, pk=item_id)
    if cur_basket[item_id] - 1 >= 1:
        cur_basket['sum'] -= basket.item.price
        cur_basket['count'] -= 1
        cur_basket[item_id] -= 1
        request.session['basket'] = cur_basket
    return redirect('shop.views.cart')

def remove_item_from_basket(request, item_id):

    cur_basket = request.session['basket']
    basket = Basket(item_id=item_id, count=1)
    item = get_object_or_404(Item, pk=item_id)
    if item_id in cur_basket:
        cur_basket['sum'] -= (basket.item.price * cur_basket[item_id])
        cur_basket['count'] -= cur_basket[item_id]
        del cur_basket[item_id]
        request.session['basket'] = cur_basket
    if cur_basket['count'] == 0:
        return redirect('shop.views.index')
    return redirect('shop.views.cart')


def make_order(request):

    user = request.user

    if request.method == 'POST':
        detail_id = request.POST.get('order_type')
        request.session['detail_id'] = detail_id
        return redirect('shop.views.confirm')
    details = DeliveryDetail.objects.all().order_by('id')
    context = {'user': user, 'details': details}
    return render(request, 'shop/order.html', context)

def confirm(request):
    user = request.user
    detail_id = request.session['detail_id']
    detail = DeliveryDetail.objects.filter(id=detail_id)[0]
    cur_basket = request.session['basket']

    cart = get_cart(cur_basket)
    if request.method == 'POST':
        order = Order(user_id=user.id, full_sum=cur_basket['sum'] + detail.tax, delivery=detail.__unicode__(),
                      order_date=datetime.now(), detail='prepare', code=Order.code_generator())
        order.save()
        for item in cart:
            item.order_id = order.id
            item.save()
        order.save()
        del request.session['basket']
        return redirect('shop.views.index')
    days = 0
    for item in cart:
        if item.item.available == 'order' or item.count > item.item.count:
            if item.item.delivery_period > days:
                days = item.item.delivery_period
    days += detail.delivery_period
    summary = cur_basket['sum'] + detail.tax
    context = {'user': user, 'detail': detail, 'cart': cart, 'days': days, 'summary': summary}
    return render(request, 'shop/confirm.html', context)


def user_orders(request, user_id):
    user = request.user
    orders = Order.objects.filter(user_id=user_id).order_by('detail')
    context = {'user': user, 'orders': orders}
    return render(request, 'shop/orders.html', context)


def reject(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    order.detail = 'rejected'
    order.save()
    return redirect('shop.views.index')
# Create your views here.
