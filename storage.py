import cmd
from source.storageController import StorageController


class Cli(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = ">>> "
        self.intro = "Добро пожаловать\nДля справки наберите 'help'"
        self.doc_header = "Доступные команды" \
                          + "(для справки по конкретной команде наберите" \
                          + " 'help _команда_')"
        self.storage = None

    def default(self, line):
        print("Несуществующая команда")

    def do_create(self, arg):
        'Создает локальное хранилище: create <directory>'
        args = self.parse(arg)
        self.storage = StorageController.create_storage(args[0])

    def do_init(self, arg):
        'Иницилизирует существующее локальное хранилище: init <directory>'
        args = self.parse(arg)
        self.storage = StorageController(args[0])

    def do_write(self, arg):
        'Записывает данные в текущее хранилище: write <key> <value>'
        args = self.parse(arg)
        self.storage.write(args[0], args[1])

    def do_read(self, arg):
        'Считывает данные из текущего хранилища: read <key>'
        args = self.parse(arg)
        print(self.storage.read(args[0]))

    def do_delete_key(self, arg):
        'Удаляет данные из текущего хранилища: delete_key <key>'
        args = self.parse(arg)
        self.storage.delete_key(args[0])

    def do_delete(self, arg):
        'Удаляет текущее хранилище: delete'
        self.storage.delete_source()

    def do_check_key(self, arg):
        'Проверяет наличие ключа в текущем хранилище: check_key <key>'
        print("Ключ есть") if self.parse(arg)[0] in self.storage \
            else print("Ключа нет")

    def do_keys(self, arg):
        'Выводит ключи из текущего хранилища: key'
        for i in self.storage:
            print(i, end=", ")
        print()

    def do_exit(self, arg):
        'выход из программы'
        print("Пока")
        return True

    @staticmethod
    def parse(arg):
        return tuple(map(str, arg.split()))


if __name__ == '__main__':
    cli = Cli()
    try:
        cli.cmdloop()
    except KeyboardInterrupt:
        print("завершение сеанса...")
