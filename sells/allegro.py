from zeep import Client
from .models import Countries,Shipment


class Allegro():

    def __init__(self, allegro_credentials, wsdl='https://webapi.allegro.pl/service.php?wsdl'):
        self.credentials=allegro_credentials
        self.wsdl=wsdl
        self.sessionId=None
        self.client = Client(self.wsdl)

    def _login(self):

        version = [i for i in self.client.service.doQueryAllSysStatus(1, self.credentials.webkey) if i.countryId == 1][0].verKey
        self.sessionId = self.client.service.doLogin(self.credentials.login, self.credentials.password, 1,
                                                self.credentials.webkey,version).sessionHandlePart

    def update_shipment_types(self):
        allegroShipments = self.client.service.doGetShipmentData(1, self.credentials.webkey)
        shipemntTypes = [Shipment(id=s.shipmentId,name=s.shipmentName
                                  ,type=s.shipmentType,
                                  time_from=s.shipmentTime.shipmentTimeFrom,
                                  time_to=s.shipmentTime.shipmentTimeTo) for s in allegroShipments.shipmentDataList.item]
        for s in shipemntTypes:
            s.save()
        return shipemntTypes

    def update_countries(self):
        countries = [Countries(id=c.countryId, name=c.countryName) for c in self.client.service.doGetCountries(1, self.credentials.webkey)]
        for c in countries:
            c.save()
        return countries
