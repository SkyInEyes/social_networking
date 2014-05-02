from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from shop.models import DeliveryDetail

@dajaxice_register
def place_information(request, place_id=''):
    place = DeliveryDetail.objects.filter(id=place_id)[0]
    if place.id == 1:
        return simplejson.dumps({'id': '1'})
    return simplejson.dumps({'address': '%s' % place.full_address, 'how_to_go': '%s' % place.how_to_go,
                             'operation_time': '%s' % place.operation_time, 'photo': '%s' % place.photo.url,
                             'id': '%s' % place.id})