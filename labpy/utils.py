import jsbeautifier
import json

_unit_map = {
    'n': 1e-9, 'u': 1e-6, 'm': 1e-3, 'k': 1e3
}

def str_to_value(s):
    v, u = s.split()
    if len(u) == 1:
        mult = 1.
    else:
        mult = _unit_map[u[0]]
    return float(v) * mult

def json_dumps_compact(data):
    opts = jsbeautifier.default_options()
    opts.indent_size = 2
    return jsbeautifier.beautify(json.dumps(data), opts)
