class ScpiParser:

    def __init__(self):
        self._commands = {}
        self._aliases = {}

    def register(self, cmd_form, fun):
        cmd = cmd_form.split(':')        
        for long_form in cmd:
            short_form =  ''.join(c for c in long_form if not c.islower())
            short_lc, long_lc = short_form.lower(), long_form.lower()
            if short_lc != long_lc and any(e.isupper() for e in short_form):
                self._aliases[short_lc] = long_lc
        cmd_expand = cmd_form.lower()
        self._commands[cmd_expand] = fun

    def _execute_task(self, task):
        cmd, args = task
        if "" in cmd or "" in args:
            # print("Improper command: empty values in", task)
            return
        cmd_lc = [c.lower() for c in cmd]
        cmd_full = [self._aliases.get(c, c) for c in cmd_lc]
        cmd_expand = ":".join(cmd_full)
        if cmd_expand in self._commands:
            return self._commands[cmd_expand](args)

    def _parse(self, data):
        cmd_tree = []
        tasks = []
        tasks_raw = [e for e in data.strip().split(';') if e.strip()]
        for task in tasks_raw:
            cmd_raw, args_raw = (task.strip() + ' ').split(' ', 1)
            cmd = cmd_raw.split(':')
            if cmd[0] and cmd[0][0] == "*":
                pass
            elif cmd[0]:
                cmd = cmd_tree + cmd
            else:
                cmd = cmd[1:]
            cmd_tree = cmd[:-1]
            args = []
            args_raw = args_raw.strip(",")
            if args_raw:
                args = [arg.strip() for arg in args_raw.split(',')]
            tasks.append([cmd, args])
        return tasks

    def _stringify(self, repl):
        if isinstance(repl, list) or isinstance(repl, tuple):
            return ','.join([str(v) for v in repl])
        else:
            return str(repl)

    def process(self, data):
        tasks = self._parse(data)
        repls = []
        for task in tasks:
            repl = self._execute_task(task)
            if repl:
                repls.append(self._stringify(repl))
        # print(tasks)
        return ';'.join(repls)


def _echo(args):
    return ','.join(args)

if(__name__ == "__main__"):
    parser = ScpiParser()
    parser.register("MEASure?", _echo)
    parser.register("MEASure", _echo)
    print(parser.process("measure:stuff volt; *RST 1; :yolo"))