# coding=utf-8
import pprint
from collections import OrderedDict

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
from .models import AllegroCredentials, Sells


@login_required(login_url='/login/')
def index(request):
    sells = Sells.objects.all().order_by('-dealDate')

    zamowienia = OrderedDict()
    for s in sells:
        temp_dict={}
        row = s.kontrachent.to_excel_row()
        row.extend(s.to_excel_row())
        row.extend(["" for x in range(8)])
        temp_dict['sells'] = s
        temp_dict['items'] = []
        for i in s.solditems_set.filter(sells=s):
            pprint.pprint(i)
            r = i.auctions.to_excel_row()
            r[1] = i.count
            row.extend(r)
            temp_dict['items'].append(i)

        zamowienia[s.allegro_id] = {'excel' : row, 'object': temp_dict}

    pprint.pprint(zamowienia)
    return render(request, 'sells/sells.html', {"zamowienia": zamowienia})

@login_required(login_url='/login/')
def news(request):
    pprint.pprint("Cos tam")
    allegroCredentials = AllegroCredentials.objects.get(login="anielskistyl")
    zamowienia = allegroCredentials.main()
    return index(request)