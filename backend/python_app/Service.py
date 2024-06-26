import abc
import requests
# from ..db.DataBaseHelper import DataBaseHelper
# from ...python_app.db.DataBaseHelper import DataBaseHelper
from DataBaseHelper import DataBaseHelper


class Service(metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__

    def criar_objeto_requisicao(self):
        pass

    def realizar_requisicao(self):
        pass

    def tratar_dados_requisicao(self):
        pass

    def enviar_dados(self):
        pass

    def apagar_dados_destino(self):
        pass


class MarsService(Service):
    def __init__(self, api_key, url_mars, sol_mars, page, alias):
        super().__init__
        self.api_key = api_key
        self.url_mars = url_mars
        self.sol_mars = sol_mars
        self.page = page
        self.alias = alias

    def criar_objeto_requisicao(self):
        return {
            'api_key': self.api_key,
            'sol': self.sol_mars,
            'page': self.page
        }

    def apagar_dados_destino(self, cursor):
        cursor.execute(f"DELETE FROM {self.alias}")

    def realizar_requisicao(self):
        obj_req = self.criar_objeto_requisicao()
        return requests.get(self.url_mars, obj_req).json()['photos']

    def tratar_dados_requisicao(self):
        lista_mars = self.realizar_requisicao()

        return [(obj['rover']['name'], obj['img_src'], obj['earth_date'])
                for obj in lista_mars]

    def enviar_dados(self):
        conn = DataBaseHelper.getConn(host='localhost', psw='',
                                      user='root', port=3306,
                                      database='nasa_api')
        cursor = conn.cursor()

        dados_envio = self.tratar_dados_requisicao()
        self.apagar_dados_destino(cursor)
        cursor.executemany("INSERT INTO mars (rover, img_src, earth_date) VALUES (%s, %s, %s)",
                           dados_envio)
        conn.commit()
        conn.close()


class ApodService(Service):
    def __init__(self, api_key, url_apod, hd, alias, start_date, end_date):
        super().__init__
        self.api_key = api_key
        self.url_apod = url_apod
        self.hd = hd
        self.alias = alias
        self.start_date = start_date
        self.end_date = end_date

    def criar_objeto_requisicao(self):
        return {
            'api_key': self.api_key,
            'hd': self.hd,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date)
        }

    def apagar_dados_destino(self, cursor):
        cursor.execute(f"DELETE FROM {self.alias}")

    def realizar_requisicao(self):
        obj_req = self.criar_objeto_requisicao()
        return requests.get(self.url_apod, obj_req).json()

    def tratar_dados_requisicao(self):
        lista_apod = self.realizar_requisicao()

        for obj in lista_apod:
            obj.pop('copyright', None)
            obj.pop('media_type', None)
            obj.pop('service_version', None)
            obj.pop('hdurl', None)

        return [(obj['date'], obj['title'], obj['explanation'], obj['url'])
                for obj in lista_apod]

    def enviar_dados(self):
        conn = DataBaseHelper.getConn(host='localhost', psw='',
                                      user='root', port=3306, 
                                      database='nasa_api')
        cursor = conn.cursor()

        dados_envio = self.tratar_dados_requisicao()
        self.apagar_dados_destino(cursor)
        cursor.executemany("INSERT INTO apod (date, title, explanation, url) VALUES (%s, %s, %s, %s)",
                           dados_envio)
        conn.commit()
        conn.close()
