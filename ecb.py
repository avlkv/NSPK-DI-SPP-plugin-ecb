"""
Парсер плагина SPP

1/2 документ плагина
"""
import logging
import os
import time
from datetime import datetime
from src.spp.types import SPP_document
from bs4 import BeautifulSoup
import requests
from lxml import etree
from selenium.webdriver.common.by import By

class ECB:
    """
    Класс парсера плагина SPP

    :warning Все необходимое для работы парсера должно находится внутри этого класса

    :_content_document: Это список объектов документа. При старте класса этот список должен обнулиться,
                        а затем по мере обработки источника - заполняться.


    """

    SOURCE_NAME = 'ecb'
    HOST = 'https://www.ecb.europa.eu'
    url_template = f'{HOST}/pub/'
    date_begin = datetime(2019, 1, 1)

    _content_document: list[SPP_document]

    def __init__(self, webdriver, *args, **kwargs):
        """
        Конструктор класса парсера

        По умолчанию внего ничего не передается, но если требуется (например: driver селениума), то нужно будет
        заполнить конфигурацию
        """
        # Обнуление списка
        self._content_document = []

        self.driver = webdriver

        # Логер должен подключаться так. Вся настройка лежит на платформе
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug(f"Parser class init completed")
        self.logger.info(f"Set source: {self.SOURCE_NAME}")
        ...

    def content(self) -> list[SPP_document]:
        """
        Главный метод парсера. Его будет вызывать платформа. Он вызывает метод _parse и возвращает список документов
        :return:
        :rtype:
        """
        self.logger.debug("Parse process start")
        self._parse()
        self.logger.debug("Parse process finished")
        return self._content_document

    def _parse(self):
        """
        Метод, занимающийся парсингом. Он добавляет в _content_document документы, которые получилось обработать
        :return:
        :rtype:
        """
        # HOST - это главная ссылка на источник, по которому будет "бегать" парсер
        self.logger.debug(F"Parser enter to {self.HOST}")

        # ========================================
        # Тут должен находится блок кода, отвечающий за парсинг конкретного источника
        # -
        pages = ['research/working-papers/html/index.en.html',
                 'research/discussion-papers/html/index.en.html',
                 'research/occasional-papers/html/index.en.html',
                 'research/legal-working-papers/html/index.en.html',
                 'research/statistics-papers/html/index.en.html',
                 'economic-research/resbull/html/index.en.html']
        for page_source in pages:
            self.logger.info(f'Загрузка страницы: {self.url_template}{page_source}')
            self.driver.get(url=f"{self.url_template}{page_source}")
            time.sleep(5)
            response = requests.get(url=f"{self.url_template}{page_source}")
            try:
                if response.status_code == 200:
                    self._parse_page()
                else:
                    self.logger.error('Не удалось загрузить страницы')
            except Exception as _ex:
                print(_ex)
        # Логирование найденного документа
        # self.logger.info(self._find_document_text_for_logger(document))

        # ---
        # ========================================
        ...

    def _parse_page(self):
        number = 0
        checker_1 = True
        length = 0

        while checker_1:
            page = self.driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            new_soup = BeautifulSoup(soup
                                     .find('main')
                                     .find('div', class_='definition-list -filter')
                                     .find('dl', class_='ecb-basicList wpSeries ecb-lazyload pub-list-filter')
                                     .prettify(), 'html.parser')
            div = new_soup.find('div', id=f'snippet{number}')
            if div != None:
                current_element = self.driver.find_element(By.ID, f'snippet{number}')
                # self.driver.execute_script(f"window.scrollTo(0, {length})")
                self.driver.execute_script("arguments[0].scrollIntoView();", current_element)
                number = number + 1
            else:
                checker_1 = False

        checker_1 = True
        number = 0

        while checker_1:
            page = self.driver.page_source
            soup = BeautifulSoup(page, 'html.parser')
            new_soup = BeautifulSoup(soup
                                     .find('main')
                                     .find('div', class_='definition-list -filter')
                                     .find('dl', class_='ecb-basicList wpSeries ecb-lazyload pub-list-filter')
                                     .prettify(), 'html.parser')

            checker_2 = True
            print(f"snippet{number}")
            div = new_soup.find('div', id=f'snippet{number}')
            number = number + 1
            if div != None:
                dt_all = div.find_all('dt', recursive=False)
                dd_all = div.find_all('dd', recursive=False)
                for i in range(len(dd_all)):
                    dd = dd_all[i]
                    dt = dt_all[i]
                    if dd != None and dt != None:
                        div_title = dd.find('div', class_='title')
                        div_authors = dd.find('div', class_='authors').find('ul')
                        div_accordion = dd.find('div', class_='accordion').find('div', class_='content-box')
                        title = div_title.find('a').get_text()
                        abstract = div_accordion.find_next('dd').get_text()
                        web_link = f"{self.HOST}{div_title.find('a').get('href')}"
                        other_data = {}
                        if div_authors != None:
                            authors = []
                            for li in div_authors.find_next('li', recursive=False):
                                authors.append(li.get_text())
                            other_data['authors'] = authors
                        pub_date = datetime.strptime(dt.get('isodate'), '%Y-%m-%d')

                        document = SPP_document(
                            None,
                            title=title,
                            abstract=abstract if abstract else None,
                            text=None,
                            web_link=web_link,
                            local_link=None,
                            other_data=other_data if other_data != {} else None,
                            pub_date=pub_date,
                            load_date=None,
                        )
                        self._content_document.append(document)
                        # print(document)
                        self.logger.debug(self._find_document_text_for_logger(document))
                        time.sleep(1)
            else:
                checker_1 = False

    @staticmethod
    def _find_document_text_for_logger(doc: SPP_document):
        """
        Единый для всех парсеров метод, который подготовит на основе SPP_document строку для логера
        :param doc: Документ, полученный парсером во время своей работы
        :type doc:
        :return: Строка для логера на основе документа
        :rtype:
        """
        return f"Find document | name: {doc.title} | link to web: {doc.web_link} | publication date: {doc.pub_date}"

    @staticmethod
    def some_necessary_method():
        """
        Если для парсинга нужен какой-то метод, то его нужно писать в классе.

        Например: конвертация дат и времени, конвертация версий документов и т. д.
        :return:
        :rtype:
        """
        ...

    @staticmethod
    def nasty_download(driver, path: str, url: str) -> str:
        """
        Метод для "противных" источников. Для разных источника он может отличаться.
        Но основной его задачей является:
            доведение driver селениума до файла непосредственно.

            Например: пройти куки, ввод форм и т. п.

        Метод скачивает документ по пути, указанному в driver, и возвращает имя файла, который был сохранен
        :param driver: WebInstallDriver, должен быть с настроенным местом скачивания
        :_type driver: WebInstallDriver
        :param url:
        :_type url:
        :return:
        :rtype:
        """

        with driver:
            driver.set_page_load_timeout(40)
            driver.get(url=url)
            time.sleep(1)

            # ========================================
            # Тут должен находится блок кода, отвечающий за конкретный источник
            # -
            # ---
            # ========================================

            # Ожидание полной загрузки файла
            while not os.path.exists(path + '/' + url.split('/')[-1]):
                time.sleep(1)

            if os.path.isfile(path + '/' + url.split('/')[-1]):
                # filename
                return url.split('/')[-1]
            else:
                return ""
