class DataList(list):
    def __init__(self, init=[]):
        super().__init__(init)
        if hasattr(init, '__dict__'):
            for k, v in init.__dict__.items():
                self.__dict__[k] =v

    def __getitem__(self, idx):
        if isinstance(idx, str):
            return [el[idx] for el in super().__iter__()]
        elif isinstance(idx, (list, tuple)):
            # Explicit super() because of list comprehension scoping
            return [[el[id] for el in super(DataList, self).__iter__()] for id in idx]
        else:
            return super().__getitem__(idx)
    def __repr__(self) -> str:
        resp = 'Meta:\n' + self.meta.__repr__()
        if len(self) < 3:
            resp += '\nData:\n' +  super().__repr__()
        else:
            resp += '\nData:\n' + self[0].__repr__() + f'\n... {len(self) - 2} ...\n' + self[-1].__repr__()
        return resp
    @property
    def meta(self):
        return self.__dict__
    @property
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

    @staticmethod
    def _recursive_copy(dic):
        for k, v in dic.items():
            if isinstance(v, dict):
                dic[k] = v.copy()
                NestedDict._recursive_copy(dic[k])

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
        super().__init__(dict)
        NestedDict._recursive_copy(self)
        self.shadow = {}


    def copy(self):
        return NestedDict(self)

    def get(self, idx, dflt=None):
        try:
            return self[idx]
        except KeyError:
            return dflt

    def __getitem__(self, idx):
        if isinstance(idx, list):
            idx = tuple(idx)
        if isinstance(idx, tuple):
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

class Average:

    def __init__(self, v = None):
        if v is not None:
            self.sum = v * 1.
        self.count = 0 if v is None else 1

    def add(self, v):
        if self.count == 0:
            self.sum = v * 1.
        else:
            self.sum += v
        self.count += 1

    @property
    def value(self):
        if self.count == 0:
            return 0.
        return self.sum / self.count

from .series import Series
