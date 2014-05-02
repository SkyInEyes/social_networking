from django.conf.urls import patterns, url, include

from shop import views

urlpatterns = patterns('',
    # ex: /polls/
    url(r'^$', views.index, name='index'),
    # ex: /polls/5/
    url(r'^(?P<item_id>\d+)/$', views.product, name='product'),
    # ex: /shop/5/add_to_basket/
    url(r'^(?P<item_id>\d+)/add_to_basket/$', views.add_to_basket, name='add_to_basket'),
    url(r'cart/$', views.cart, name='cart'),
    url(r'^(?P<item_id>\d+)/remove_count_in_basket/$', views.remove_count_in_basket, name='remove_count_in_basket'),
    url(r'^(?P<item_id>\d+)/add_count_in_basket/$', views.add_count_in_basket, name='add_count_in_basket'),
    url(r'^(?P<item_id>\d+)/remove_item_from_basket/$', views.remove_item_from_basket, name='remove_from_basket'),
    url(r'order/$', views.make_order, name='make_order'),
    url(r'confirm/$', views.confirm, name='confirm'),
    url(r'^(?P<user_id>\d+)/orders/$', views.user_orders, name='user_orders'),
    url(r'^(?P<order_id>\d+)/reject/$', views.reject, name='delete_order'),
    # ex: /polls/5/vote/
    #url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
)