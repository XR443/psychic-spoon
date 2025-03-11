from abc import ABC, abstractmethod

from media import Media


class Storage(ABC):

    @abstractmethod
    def save(self, media: Media):
        """
        Сохранение файла в хранилище

        :param media: Файл для сохранения
        :return: Ид сохраненного файла
        """
        pass

    @abstractmethod
    def load(self, id) -> Media:
        """
        Получение файла из хранилища

        :param id: Ид сохраненного файла
        :return: Медиа-файл
        """
        pass
