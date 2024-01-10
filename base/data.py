import json
import re
import traceback
from typing import Iterator

from base.log import logger


class _localStore:
    """
    A local file store.
    """

    def __init__(self, filepath: str, default: int | str | dict | list) -> None:
        self.filepath = filepath
        self.default = default
        self.load()

    def load(self) -> None:
        """
        Load data from file.
        """
        try:
            with open(self.filepath, 'r') as f:
                self.data = json.load(f)
        except Exception as e:
            logger.warning(f'Failed to load data, use default. {self.filepath}, {e}')
            logger.debug(traceback.format_exc())
            self.data = self.default
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f)

    def __dump_check(self, format=True) -> bool:
        """
        Check if the data can be dumped.
        :param format: format json
        :return: True if the data can be dumped, False otherwise
        """
        try:
            if format:  # format json
                json.dumps(self.data,
                           ensure_ascii=False, sort_keys=True, indent=4, default=str)
            else:
                json.dumps(self.data, default=str)
            return True
        except Exception as e:
            logger.warning(f'Failed to dump data. {self.filepath}, {e}')
            logger.debug(traceback.format_exc())
            return False

    def dump(self, format=True) -> None:
        """
        Dump data to file.
        :param format: format json
        """
        if not self.__dump_check(format):  # check if the data can be dumped
            return
        try:
            with open(self.filepath, 'w') as f:
                if format:
                    json.dump(self.data, f,
                              ensure_ascii=False, sort_keys=True, indent=4, default=str)
                else:
                    json.dump(self.data, f, default=str)
        except Exception as e:
            logger.error(f'Failed to dump data to file. {self.filepath}, {e}')
            logger.debug(traceback.format_exc())

    def update(self, value: int | str | dict | list, update=True) -> None:
        self.data = value
        update and self.dump()

    def __iter__(self) -> Iterator:
        return iter(self.data)

    def __len__(self) -> int:
        return len(self.data)

    def clear(self, update=True) -> None:
        self.data.clear()
        update and self.dump()


class localDict(_localStore):
    def __init__(self, name: str, default: dict = None, folder='data', digit_mode=False) -> None:
        if default is None:
            default = {}
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)
        if digit_mode:  # convert dict keys to int
            self.data = {int(k): v for k, v in self.data.items()}

    def __getitem__(self, key: str | int) -> object | None:
        return self.data.get(key, None)

    def __setitem__(self, key: str | int, value: object) -> None:
        self.data[key] = value

    def __delitem__(self, key: str | int) -> None:
        if key in self.data:
            del self.data[key]

    def __contains__(self, key: str | int) -> bool:
        return key in self.data

    def keys(self) -> list:
        return self.data.keys()

    def values(self) -> list:
        return self.data.values()

    def get(self, key: str | int) -> object:
        return self.data.get(key)

    def items(self) -> list:
        return self.data.items()

    def set(self, key: str | int, value: object, update=True) -> None:
        self.data[key] = value
        update and self.dump()

    def delete(self, key: str | int, update=True) -> None:
        if key in self.data:
            del self.data[key]
        update and self.dump()


class localList(_localStore):
    def __init__(self, name: str, default: list = None, folder: str = 'data') -> None:
        if default is None:
            default = []
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)

    def __getitem__(self, index: int | slice) -> object:
        return self.data[index]

    def __setitem__(self, index: int | slice, item: object) -> None:
        self.data[index] = item

    def __delitem__(self, index: int | slice) -> None:
        del self.data[index]

    def __contains__(self, item: object) -> bool:
        return item in self.data

    def set(self, index: int, item: object, update=True) -> None:
        self.data[index] = item
        update and self.dump()

    def append(self, item: object, update=True) -> None:
        self.data.append(item)
        update and self.dump()

    def remove(self, item: object, update=True) -> None:
        self.data.remove(item)
        update and self.dump()


class localStr(_localStore):
    def __init__(self, name: str, default: str = None, folder: str = 'data') -> None:
        if default is None:
            default = ''
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)


class localInt(_localStore):
    def __init__(self, name: str, default: int = 0, folder: str = 'data') -> None:
        filepath = folder + '/' + name + '.json'
        super().__init__(filepath, default)
        self.data = int(self.data)


class localCookies:
    """
    Local cookies.
    """

    def __init__(self, name, fields) -> None:
        """
        :param name: file name
        :param fields: fields to be stored
        """
        self.valid = True
        self.fields = fields
        self.data = localDict(name, {x: '' for x in fields}, folder='secret')

    def get(self) -> str:
        """
        Get cookies.
        """
        return '; '.join(f'{k}={v}' for k, v in self.data.items())

    def update(self, content):
        """
        Update cookies.
        """
        for field in self.fields:
            r = re.search(f'{field}=([^;]+)', content)
            if r is not None:
                self.data[field] = r.group(1)
        self.data.dump()
        self.valid = True

    def expired(self):
        """
        Check if the cookies is expired.
        """
        self.valid = False
