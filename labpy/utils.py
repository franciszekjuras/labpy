import jsbeautifier
import json

_unit_map = {
    'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'k': 1e3
}

def _split_unit(s:str):
    for i in range(len(s)):
        if s[i].isalpha():
            break
    return s[:i].strip(), s[i:].strip()

def str_to_value(s, base=1.):
    v, u = _split_unit(s)
    if len(u) == 1:
        mult = 1.
    else:
        mult = _unit_map[u[0]]
        mult /= base
    return float(v) * mult

def json_dumps_compact(data):
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    return jsbeautifier.beautify(json.dumps(data), opts)

def check_type(types, *vars):
    for v in vars:
        if not isinstance(v, types):
            raise TypeError(f"{type(v)} is not of type(s) {types}")

def floatify(v, precision=6):
    if isinstance(v, int):
        return (str(v) + '.0')
    if isinstance(v, float):
        if v.is_integer():
            return str(v)
        return (f"{v:.{precision}f}".rstrip('0'))
    raise TypeError(f"Variable of type {type(v)} is not a float" )

def intify(v):
    if isinstance(v, int):
        return str(v)
    raise TypeError(f"Variable of type {type(v)} is not an integer" )

def to_enum(v, Type):
    if isinstance(v, str):
        return Type[v.upper().replace(' ','_')]
    return Type(v)

def list_visa_devices(rm):
    res = [(str(inst.alias), str(inst.resource_name)) for inst in rm.list_resources_info().values()]
    res.insert(0, ("Alias", "Resource name"))
    for el in res:
        print(f"{el[0]:>15}  {el[1]}")
