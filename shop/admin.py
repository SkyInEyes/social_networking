from django import forms
from django.contrib import admin
from shop.models import Item, Order, Basket, Photo, Thumb, WriteComment, DeliveryDetail
from django.contrib.auth.models import User


class PhotoInLine(admin.StackedInline):
    model = Photo
    extra = 5


class ThumbInLine(admin.StackedInline):
    model = Thumb

class CommentInLine(admin.StackedInline):
    model = WriteComment
    extra = 10

class ItemAdmin(admin.ModelAdmin):

    inlines = [ThumbInLine] + [PhotoInLine] + [CommentInLine]


class BasketInline(admin.StackedInline):
    model = Basket
    extra = 3


class UserInLine(admin.StackedInline):
    model = User
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    inlines = [BasketInline]


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(WriteComment)
admin.site.register(DeliveryDetail)
