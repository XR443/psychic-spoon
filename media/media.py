from abc import ABC, abstractmethod


class Media(ABC):
    def __init__(self, file_name, owner, created_date, **metadata):
        self.file_name = file_name
        self.owner = owner
        self.data = None
        self.created_date = created_date
        self.metadata = metadata

    @abstractmethod
    def read(self):
        """
        Получение данных, хранящихся в этом медиа-файле
        
        :return: Записанные данные
        """
        pass

    @abstractmethod
    def write(self, data):
        """
        Запись данных в медиа-файл
        
        :param data: Данные для записи
        :return: None
        """
        pass


class Photo(Media):

    def read(self):
        pass

    def write(self, data):
        pass


class Video(Media):

    def read(self):
        pass

    def write(self, data):
        pass


class Audio(Media):

    def read(self):
        pass

    def write(self, data):
        pass
