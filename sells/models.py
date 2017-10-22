# coding=utf-8
import datetime
import pprint
from collections import OrderedDict
from zeep import Client
from django.db import models
import django.utils.timezone as dtimezone
import moneyed
from djmoney.models.fields import MoneyField

payu = {"m": "mTransfer - mBank",
        "mtex": "mTransfer mobilny - mBank",
        "w": "BZWBK - Przelew24",
        "o": "Pekao24Przelew - Bank Pekao",
        "i": "Płacę z Inteligo",
        "p": "Płać z iPKO",
        "pkex": "PayU Express Bank Pekao",
        "g": "Płać z ING",
        "gbx": "Płacę z Getin Bank",
        "gbex": "GetIn Bank PayU Express",
        "nlx": "Płacę z Noble Bank",
        "nlex": "Noble Bank PayU Express",
        "ib": "Paylink Idea - IdeaBank",
        "l": "Credit Agricole",
        "as": "Płacę z T-mobile Usługi Bankowe dostarczane przez Alior Bank",
        "exas": "PayU Express T-mobile Usługi Bankowe",
        "u": "Eurobank",
        "ab": "Płacę z Alior Bankiem",
        "exab": "PayU Express z Alior Bankiem",
        "ps": "Płacę z PBS",
        "wm": "Przelew z Millennium",
        "h": "Przelew z BPH",
        "wd": "Przelew z Deutsche Banku",
        "wc": "Przelew z Citi Handlowego",
        "bo": "Płać z BOŚ",
        "bnx": "Płacę z BNP Paribas",
        "bnex": "BNP Paribas PayU Express",
        "orx": "Płacę z Orange",
        "orex": "PayU Express Orange",
        "c": "Karta kredytowa",
        "b": "Przelew bankowy",
        "pu": "Konto PayU",
        "ai": "Raty PayU",
        "t": "płatność testowa",
        "blik": "Blik",
        "tt": "Karta płatnicza"}


def formatyText(message):
    if message:
        print(message)
        if message.find("\n"):
            message = message.replace("\n", " ")
        if message.find(","):
            message = message.replace(",", " ")
        return message
    return "Brak"


# Create your models here.


class LastSells(models.Model):
    sell_date = models.DateTimeField('sell_date')


class Kontrahent(models.Model):
    name = models.CharField(max_length=255)
    surename = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    post_code = models.CharField(max_length=6)
    mail = models.EmailField()
    phone = models.CharField(max_length=24)
    login = models.CharField(max_length=255)

    def __str__(self):
        return "{0} {1}".format(self.name, self.surename)

    def to_excel_row(self):
        return [formatyText("{} {}".format(self.name, self.surename)),
                "{}, {} {}".format(self.address,
                                   self.post_code, self.city),
                self.mail,
                self.phone,
                "Allegro",
                self.login
                ]


class Auctions(models.Model):
    title = models.CharField(max_length=255)
    price = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')
    external_id = models.BigIntegerField()

    def __str__(self):
        return self.title

    def to_excel_row(self):
        return [self.title, 1, self.price]



class Sells(models.Model):
    allegro_id = models.BigIntegerField()
    kontrachent = models.ForeignKey(Kontrahent)
    dealDate = models.DateTimeField(default=dtimezone.now)
    total_ammount = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')
    sells_ammount = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')
    shipment_amount = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN')
    payment_type = models.CharField(max_length=255, null=True)
    payment_amount = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN', null=True)
    payment_date = models.DateTimeField(default=dtimezone.now, null=True)
    payment_id = models.IntegerField(null=True)
    shipment_address_name = models.CharField(max_length=255)
    shipment_address_street = models.CharField(max_length=255)
    shipment_address_city = models.CharField(max_length=255)
    shipment_address_country = models.CharField(max_length=255)
    shipment_address_phone = models.CharField(max_length=255)
    shipment_describe = models.CharField(max_length=255)
    client_message = models.CharField(max_length=255)
    items = models.ManyToManyField(Auctions, through='SoldItems')
    state = models.CharField(max_length=255, default="NOWY")

    def __str__(self):
        return "{} - {}".format(self.dealDate, self.total_ammount)

    @property
    def avalible_states(self):
        if self.state == 'NOWY':
            return ['W TRAKCIE', 'ZROBIONY', 'ANULOWANY']
        if self.state == 'W TRAKCIE':
            return ['ZROBIONY', 'ANULOWANY']
        if self.state == 'ZROBIONY':
            return ['ANULOWANY']
        if self.state == 'ANULOWANY':
            return ['W TRAKCIE', 'ZROBIONY', 'ANULOWANY']
        return ['ERROR']

    def to_excel_row(self):
        pprint.pprint(type(self.dealDate))
        pprint.pprint(type(self.payment_date))
        return [
            self.dealDate.strftime("%Y-%m-%d %H:%M"),
            str(self.total_ammount),
            str(self.sells_ammount),
            str(self.shipment_amount),
            self.payment_type,
            self.payment_amount,
            "",
            self.payment_date.strftime("%d/%m/%Y") if self.payment_date else None,
            str(self.payment_id),
            "",
            self.shipment_address_name,
            self.shipment_address_street,
            self.shipment_address_city,
            self.shipment_address_country,
            self.shipment_address_phone if self.shipment_address_phone else "",
            self.shipment_describe,
            formatyText(self.client_message)
        ]


class SoldItems(models.Model):
    sells = models.ForeignKey(Sells)
    auctions = models.ForeignKey(Auctions)
    count = models.IntegerField()


class Shipment(models.Model):
    name = models.CharField(max_length=255)
    type = models.IntegerField()
    time_from = models.IntegerField()
    time_to = models.IntegerField()


class Countries(models.Model):
    name = models.CharField(max_length=255)


class AllegroCredentials(models.Model):
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    webkey = models.CharField(max_length=255)

    def generateRozliczenie(self, postBuyForm, client, shipmentTypes, countries, k_row):

        dealDates = set()
        kwotaZamowienia = 0
        items = []
        items_model = []
        for item in postBuyForm.postBuyFormItems.item:
            pprint.pprint(item)
            i, created = Auctions.objects.get_or_create(external_id=item.postBuyFormItId,
                                                        defaults={
                                                            'title': item.postBuyFormItTitle,
                                                            'price': item.postBuyFormItAmount,
                                                            'external_id': item.postBuyFormItId
                                                        })
            pprint.pprint(item.postBuyFormItPrice)
            items_model.append((item.postBuyFormItQuantity, i))
            items.append(item.postBuyFormItTitle)
            items.append(str(item.postBuyFormItQuantity))
            items.append(str(item.postBuyFormItPrice))
            items.append(str(item.postBuyFormItAmount))
            kwotaZamowienia += item.postBuyFormItAmount

            for deal in item.postBuyFormItDeals.item:
                print(deal.dealDate)
                dealDates.add(deal.dealDate)
                pprint.pprint(dealDates)
        pprint.pprint("SoldItems: {}".format(items_model))

        if postBuyForm.postBuyFormGdAddress.postBuyFormAdrFullName is None:

            shipmentInfo = postBuyForm.postBuyFormShipmentAddress
        else:
            shipmentInfo = postBuyForm.postBuyFormGdAddress
        c = dealDates.pop()
        pprint.pprint(c)
        print("Tutaj")
        pprint.pprint(postBuyForm.postBuyFormDateRecv)
        sells, created = Sells.objects.get_or_create(
            allegro_id=postBuyForm.postBuyFormId,
            defaults={
                'allegro_id': postBuyForm.postBuyFormId,
                'dealDate': c,
                'kontrachent': k_row,
                'total_ammount': postBuyForm.postBuyFormAmount,
                'sells_ammount': kwotaZamowienia,
                'shipment_amount': postBuyForm.postBuyFormPostageAmount,
                'payment_type': payu[str(postBuyForm.postBuyFormPayType)],
                'payment_amount': postBuyForm.postBuyFormPaymentAmount,
                'payment_date': datetime.datetime.strptime(postBuyForm.postBuyFormDateRecv, "%Y-%m-%d %H:%M:%S"),
                'payment_id': postBuyForm.postBuyFormPayId,
                'shipment_address_name': shipmentInfo.postBuyFormAdrFullName,
                'shipment_address_street': shipmentInfo.postBuyFormAdrStreet,
                'shipment_address_city': "{} {}".format(shipmentInfo.postBuyFormAdrPostcode,
                                                        shipmentInfo.postBuyFormAdrCity),
                'shipment_address_country': countries[shipmentInfo.postBuyFormAdrCountry],
                'shipment_address_phone': shipmentInfo.postBuyFormAdrPhone if shipmentInfo.postBuyFormAdrPhone else "",
                'shipment_describe': "{} {}".format(shipmentTypes[postBuyForm.postBuyFormShipmentId].shipmentName,
                                                    str(postBuyForm.postBuyFormPostageAmount)),
                'client_message': formatyText(postBuyForm.postBuyFormMsgToSeller)
            })

        for q, i in items_model:
            SoldItems(count=q,
                      sells=sells,
                      auctions=i
                      ).save()

        result = sells.to_excel_row()
        for si in SoldItems.objects.filter(sells=sells):
            row = si.auctions.to_excel_row()
            row[1] = si.count
            result.extend(row)
        return result

    def generateClientInfo(self, kontrachent):
        k, created = Kontrahent.objects.get_or_create(
            login=kontrachent.userLogin,
            name=kontrachent.userFirstName,
            surename=kontrachent.userLastName,
            defaults={
                'name': kontrachent.userFirstName,
                'surename': kontrachent.userLastName,
                'address': kontrachent.userAddress,
                'post_code': kontrachent.userPostcode,
                'city': kontrachent.userCity,
                'mail': kontrachent.userEmail,
                'phone': kontrachent.userPhone,
                'login': kontrachent.userLogin
            }
        )

        return (k.to_excel_row(), k)

    def main(self):
        lastevent = datetime.datetime.fromtimestamp(0)
        key = self.webkey
        password = self.password
        login = self.login
        client = Client('https://webapi.allegro.pl/service.php?wsdl')
        version = [i for i in client.service.doQueryAllSysStatus(1, key) if i.countryId == 1][0].verKey
        sessionId = client.service.doLogin(login, password, 1, key, version).sessionHandlePart
        shipemntTypes = {s.shipmentId: s for s in client.service.doGetShipmentData(1, key).shipmentDataList.item}

        countries = {c.countryId: c.countryName for c in client.service.doGetCountries(1, key)}

        journal = datetime.datetime.fromtimestamp(
            client.service.doGetSiteJournalDealsInfo(sessionId, 0).dealLastEventTime)
        zamowienia = OrderedDict()
        if lastevent < journal:
            print("Sa nowe zamowienia $_$")
            events = client.service.doGetSiteJournalDeals(sessionId)
            for idx, e in enumerate(events):
                if e.dealTransactionId > 0 and (e.dealEventType == 4 or e.dealEventType == 2):
                    zamowienia[e.dealTransactionId] = []

        pprint.pprint(zamowienia)
        for id, zamowienie in zamowienia.items():
            if not Sells.objects.filter(allegro_id=id).exists():
                postBuyFroms = client.service.doGetPostBuyFormsDataForSellers(sessionId, transactionsIdsArray=[
                    id])[0]
                kontrachentForm = client.service.doGetPostBuyData(sessionId, itemsArray=[
                    postBuyFroms.postBuyFormItems.item[0].postBuyFormItId],
                                                                  buyerFilterArray=[
                                                                      postBuyFroms.postBuyFormBuyerId])
                kontrachent = kontrachentForm[0].usersPostBuyData.item[0].userData
                (k_excel, k_row) = self.generateClientInfo(kontrachent)
                zamowienie.extend(k_excel)

                zamowienie.extend(self.generateRozliczenie(postBuyFroms, kontrachent, shipemntTypes, countries, k_row))
                # zamowienia[postBuyFroms.postBuyFormId] = zamowienie
                # pprint.pprint(zamowienie)

        return zamowienia
