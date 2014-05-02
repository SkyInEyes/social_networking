# -*- coding: utf-8 -*-


import string
import random

from django.db import models
from django.contrib.auth.models import User
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.db.models.signals import post_save
from datetime import datetime


class Item(models.Model):

    name = models.CharField('Название модели', max_length=150)
    type = models.CharField('Категория', max_length=150, choices=[('Phone', 'Телефон'), ('Tablet', 'Планшет')])
    price = models.FloatField()
    mark = models.SmallIntegerField()
    description = models.TextField()
    available = models.CharField(max_length=16, choices=[('available', 'в наличии'), ('order', 'под заказ'),
                                                         ('unavailable', 'нет в наличии')])
    count = models.IntegerField()
    delivery_period = models.IntegerField('Период доставки на склад', blank=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __unicode__(self):
        return self.name

    def get_comments(self):
        return self.writecomment_set.all()

    def get_photos(self):
        return self.photo_set.all()


class Photo(models.Model):
    item = models.ForeignKey(Item)
    photo = models.ImageField(upload_to='photo')


class Thumb(models.Model):
    item = models.OneToOneField(Item, primary_key=True)
    thumb = models.ImageField(upload_to='thumb')


class Order(models.Model):

    user = models.ForeignKey(User)
    full_sum = models.FloatField(blank=True)
    delivery = models.CharField(max_length=150)
    order_date = models.DateTimeField('delivery date')
    code = models.CharField('Код заказа', max_length=10)
    detail = models.CharField(max_length=150, blank=True,
                              choices=[('prepare', 'обробатывается'), ('storage', 'на складе'),
                                       ('store', 'в пункте выдачи'), ('courier', 'у курьера'),
                                       ('delivered', 'доставлен/получен'), ('rejected', 'отклонен пользователем'),
                                       ('withdrawn', 'отозван с пункта выдачи')])

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.user.first_name

    def get_items_count(self):
        count = 0
        for item in self.basket_set.all():
            count += item.count
        return count

    @staticmethod
    def code_generator(size=10, chars=string.ascii_lowercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'




class Basket(models.Model):
    item = models.ForeignKey(Item)
    order = models.ForeignKey(Order)
    count = models.SmallIntegerField()
    sum = models.FloatField(blank=True)

    def save(self, *args, **kwargs):
        self.sum = self.item.price * self.count
        if self.item.count > 0:
            self.item.count -= self.count
            if self.item.count <= 0:
                self.item.count = 0
                self.item.available = 'order'
        self.item.save()
        super(Basket, self).save(*args, **kwargs)


class WriteComment(models.Model):
    item = models.ForeignKey(Item)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=150)
    comment = models.TextField()
    comment_date = models.DateTimeField('Дата комментария')
    mark = models.SmallIntegerField(blank=True)

    def __unicode__(self):
        return self.item.name + ' ' + str(self.comment_date)

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'


class DeliveryDetail(models.Model):
    type = models.CharField('Способ доставки', max_length=32,
                            choices=[('self', 'Пункт выдачи заказов'), ('courier', 'Курьерская')])
    tax = models.FloatField('Плата за доставку')
    address = models.CharField('Станция метро рядом с пунктом самовывоза', max_length=256, blank=True)
    delivery_period = models.IntegerField('Период доставки со склада')
    full_address = models.CharField('Адрес пункта самовывоза', max_length=1024, blank=True)
    how_to_go = models.CharField('Как добраться', max_length=1024, blank=True)
    operation_time = models.CharField('Время работы', max_length=512, blank=True)
    photo = models.ImageField(upload_to='points_map', blank=True)
    class Meta:
        verbose_name = 'Способ доставки'
        verbose_name_plural = 'Способы доставки'

    def __unicode__(self):
        if self.type == 'self':
            return self.address
        return u'Курьерская'


def update_sum(sender, instance, **kwargs):
    instance.order.full_sum += instance.sum
    instance.order.save()


def update_mark(sender, instance, **kwargs):
    instance.item.mark = 0
    for comment in instance.item.writecomment_set.all():
        instance.item.mark += comment.mark
    instance.item.mark /= len(instance.item.writecomment_set.all())
    instance.item.save()

# register the signal
post_save.connect(update_sum, sender=Basket, dispatch_uid="update_item_price")
post_save.connect(update_mark, sender=WriteComment, dispatch_uid="update_item_mark")

