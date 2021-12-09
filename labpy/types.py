from copy import deepcopy

class DataList(list):
    def __getitem__(self, idx):
        if isinstance(idx, str):
            return [el[idx] for el in super().__iter__()]
        elif isinstance(idx, (list, tuple)):
            # Explicit super() because of list comprehension scoping
            return [[el[id] for el in super(DataList, self).__iter__()] for id in idx]
        else:
            return super().__getitem__(idx)
    def __repr__(self) -> str:
        return 'Info:\n' + self.__dict__.__repr__() + '\nData:\n' + super().__repr__()
    def info(self):
        return self.__dict__
    def data(self):
        return [el for el in super().__iter__()]

class IndexedProperty:
    def _default_getter(idx):
        raise NotImplementedError("Indexed property getter not implemmented")
    def _default_setter(idx, value):
        raise NotImplementedError("Indexed property setter not implemmented")
    def __init__(self, getter=None, setter=None):
        self._getitem = getter if getter is not None else IndexedProperty._default_getter
        self._setitem = setter if setter is not None else IndexedProperty._default_setter
    def __getitem__(self, idx):
        return self._getitem(idx)
    def __setitem__(self, idx, value):
        self._setitem(idx, value)

class NestedDict(dict):

    def _resolve_path(self, path, create=False):
        parent = self
        path = list(path)
        last = path.pop()
        for idx in path:
            if create and idx not in parent:
                parent[idx] = {}
            parent = parent[idx]
        return parent, last

    def __init__(self, dict={}):
        super().__init__(deepcopy(dict))
        self.shadow = {}

    def __getitem__(self, idx):
        if isinstance(idx, (list, tuple)):
            if idx in self.shadow:
                return self.shadow[idx]
            else:
                node, idx = self._resolve_path(idx)
                return node[idx]
        else:
            return super().__getitem__(idx)

    def __setitem__(self, idx, value):
        if isinstance(idx, (list, tuple)):
            node, idx = self._resolve_path(idx, create=True)
            node[idx] = value
        else:
            return super().__setitem__(idx, value)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __repr__(self):
        if len(self.shadow) == 0:
            return super().__repr__()
        else:
            return super().__repr__() + '\nshadow: ' + self.shadow.__repr__()

from .series import Series