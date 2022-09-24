import logging
import sys

CONSOLE_LOG_FLAG = logging.WARNING


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Создание обработчика для записи данных в консоль
console_out = logging.StreamHandler(stream=sys.stdout)
console_out.setLevel(CONSOLE_LOG_FLAG)

# Создание обработчика для записи данных в файл
log_handler = logging.FileHandler('logs.log', encoding='utf-8')
log_handler.setLevel(logging.DEBUG)

# Создание Formatter для форматирования сообщений в лог-файле
handler_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(funcName)s: in %(lineno)d - %(message)s")


# '[%(asctime)s]:%(levelname)s: %(message)s'

# Создание Formatter для форматирования сообщений в консоли
console_out_formatter = logging.Formatter('%(levelname)s: %(message)s')

# Добавление Formatter в обработчики
log_handler.setFormatter(handler_formatter)
console_out.setFormatter(console_out_formatter)

# Добавление обработчик в Logger
log.addHandler(console_out)
log.addHandler(log_handler)

log.info('Programm start'.center(75, '='))
log.info('Logging setup completed.')
