# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm, TextInput, Select
from shop.models import WriteComment, Order, Basket, Item


class CommentForm(ModelForm):
    class Meta:
        model = WriteComment
        fields = ('name', 'comment', 'mark')
        widgets = {
            'mark': TextInput(attrs={'value': '0', 'id': 'mark_value', 'hidden': 'true'}),
        }


class ItemInBasketForm(forms.Form):
    name = forms.CharField(max_length=128, widget=forms.TextInput(attrs={'readonly': 'true'}))
    count = forms.IntegerField(min_value=0, widget=forms.TextInput(attrs={'hidden': 'true', 'class': 'item_count'}))
    sum = forms.FloatField(widget=forms.TextInput(attrs={'hidden': 'true', 'class': 'item_sum'}))


class SortForm(forms.Form):
    type = forms.ChoiceField(choices=[('all', u'Любой тип')] + Item._meta.get_field('type').choices)
    class Meta:
        widgets = {
            'type': Select(attrs={'onchange': 'this.form.submit()'})
        }


