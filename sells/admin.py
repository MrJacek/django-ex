from django.contrib import admin

# Register your models here.
from .models import AllegroCredentials, LastSells,Kontrahent,Countries,Shipment,Sells, Auctions, SoldItems


admin.site.register(AllegroCredentials)
admin.site.register(LastSells)
admin.site.register(Kontrahent)
admin.site.register(Countries)
admin.site.register(Shipment)
admin.site.register(Sells)
admin.site.register(Auctions)
admin.site.register(SoldItems)