import matplotlib.pyplot as plt
from pathlib import Path
from __log__ import log
import yaml

ENCODING = 'utf-8'
UNIT = 10


def straight_line_equation(value_x: float, coords_x: tuple, coords_y: tuple) -> float:
    """
    
    Нахождение ординаты прямой по абсциссе. Прямая заданна двумя точками.
    
    Args:
        value_x: значение абсциссы
        coords_x: абсциссы двух точек
        coords_y: ординаты двух точек

    Returns: значение ординаты

    """
    return (coords_y[1] - coords_y[0]) * ((value_x - coords_x[0]) / (coords_x[1] - coords_x[0])) + coords_y[0]


def read_yml_file(path: Path):
    """
    Считать данные из YAML файла

    Args:
        path: путь до файла

    Returns: содержимое файла
    """
    with open(path, "r", encoding=ENCODING) as file_data:
        return yaml.load(file_data, Loader=yaml.FullLoader)


def confirm_prompt(question: str) -> bool:
    """
    Подтверждение действия

    Args:
        question: вопрос

    Returns: подтверждение
    """

    answer = None
    while answer not in ("", "y", "ye", "yes", "n", "no"):
        answer = input(f"{question} [Y/n]: ").lower()
    return answer in ("", "y", "ye", "yes")


def str_into_tuple(string: str) -> tuple:
    """
    Прообразовать строку формы 'a,a', где a-число, в кортеж

    Args:
        string: строка формы 'a,a'

    Returns: кортеж
    """
    return tuple(map(float, string.split(',')))


def upload_new_var_data(new_data: dict, variants_data: dict) -> None:
    """
    Загрузить данные нового варианта в YAML файл

    Args:
        new_data: новые данные
        variants_data: данные считанные из файла

    Returns: None

    """
    variants_data['variants'].append(new_data)

    with open('../data/variants_data.yml', "w", encoding=ENCODING) as file:
        yaml.dump(variants_data, file, allow_unicode=True, sort_keys=False)

        log.info('Входные данные успешно обновлены!')


def get_unique_variant(var_num: int, variants_data: dict) -> dict:
    """
    Получить уникальный вариант

    Args:
        var_num: номер варианта
        variants_data: данные, считанные из файла YAML

    Returns: данные варианты

    """
    for item in variants_data['variants']:
        if item.get('Номер варианта') == var_num:
            return item

    log.error(f'Вариант №{var_num} не найден!')


def add_new_variant(var_num: int, variants_data: dict):
    """

    Добавить новые данные

    Args:
        var_num: номер варианта
        variants_data: данные всех вариантов

    Returns: None

    """

    answer = confirm_prompt('\nВы хотите добавить данные для этого варианта?')

    if answer:
        upload_new_var_data({
            'Номер варианта': var_num,
            'Pст.пос, [Н]': int(input(f'\nPст.пос, [Н]: ')),
            'Pст.взл, [Н]': int(input(f'Pст.взл, [Н]: ')),
            'Aэ, [Дж]': int(input(f'Aэ, [Дж]: ')),
            'G0/Gпос, [-]': float(input(f'G0/Gпос, [-]: ')),
            'Vпос, [км/ч]': int(input(f'Vпос, [км/ч]: ')),
            'Vвзл, [км/ч]': int(input(f'Vвзл, [км/ч]: ')),
            'p0 * 10^5, [Па]': float(input(f'p0 * 10 ^ 5, [Па]: ')),
            'Индекс шасси': str(input(f'Индекс шасси: ')),
        }, variants_data)


def pneumatics_selection(pneumatics: dict, var_data: dict, amount_wheels: int):
    """

    Подбор пневматика

    Args:
        pneumatics: данные всех пневматиков
        var_data: данные варианта
        amount_wheels: кол-во колёс стойки шасси

    Returns: данные подобранного пневматика

    """

    for item in pneumatics["pneumatics"]:
        if ((var_data['Pст.пос, [Н]'] / (UNIT * amount_wheels) < item["Pст.пос, [кгс]"]) &
            (var_data['Pст.взл, [Н]'] / (UNIT * amount_wheels) < item["Pст.взл, [кгс]"]) &
            (var_data['Vвзл, [км/ч]'] / amount_wheels < item["Vвзл, [км/ч]"]) &
            (var_data['Vпос, [км/ч]'] / amount_wheels < item["Vпос, [км/ч]"])) & \
                (str_into_tuple(item["p0, [кгс/см^2]"])[0] <= var_data["p0 * 10^5, [Па]"]
                 <= str_into_tuple(item["p0, [кгс/см^2]"])[1]):
            return item


def lines(axis, coords_x, coords_y, options: dict):
    axis.vlines(coords_x[0], 0, coords_y[0], **options)
    axis.hlines(coords_y[0], 0, coords_x[0], **options)

    axis.vlines(coords_x[1], 0, coords_y[1], **options)
    axis.hlines(coords_y[1], 0, coords_x[1], **options)


def plot(pneumatic_data: dict, value_p0: float):
    """

    Построение графика

    Args:
        pneumatic_data: данные подобранного пневматика
        value_p0: значение p0

    Returns: None

    """

    font = {'family': 'serif',
            'color': 'black',
            'weight': 'normal',
            'size': 16,
            }

    figure, axis = plt.subplots(figsize=(12, 8))
    figure.subplots_adjust(right=0.75)

    plt.title(r'Определение $A_{м.д.}$, $\delta_{м.д.}$, $P_{м.д.}$', fontdict=font)

    crimping = axis.twinx()
    force = axis.twinx()

    force.spines.right.set_position(("axes", 1.2))

    log.warning("Введённые данные возможно некорректные")

    pressure_vals = str_into_tuple(pneumatic_data["p0, [кгс/см^2]"])
    work_vals = str_into_tuple(pneumatic_data["Aм.д, [кг*м]"])
    crimping_vals = str_into_tuple(pneumatic_data["delta_м.д, [мм]"])
    force_vals = str_into_tuple(pneumatic_data["Pм.д, [кгс]"])

    p1, = axis.plot(pressure_vals, work_vals, "b", label="Максимально допустимая работа", linewidth=3, linestyle='-')
    p2, = crimping.plot(pressure_vals, crimping_vals, "r", label="Максимально допустимое обжатие", linewidth=3,
                        linestyle='-.')
    p3, = force.plot(pressure_vals, force_vals, "g", label="Максимально допустимая сила", linewidth=3, linestyle='--')

    FITTING = 1.2

    axis.set_xlim(pressure_vals[0] - sum(pressure_vals) // 6, FITTING * max(pressure_vals))
    axis.set_ylim(work_vals[0] - sum(work_vals) // 6, FITTING * max(work_vals))
    crimping.set_ylim(crimping_vals[0] - sum(crimping_vals) // 6, FITTING * max(crimping_vals))
    force.set_ylim(force_vals[0] - sum(force_vals) // 4, FITTING * max(force_vals))

    axis.set_xlabel(r"$p_0, [{кгс}/{см^2}]$", fontdict=font)
    axis.set_ylabel(r"$A_{мд}, [даН * мм]$", fontdict=font)
    crimping.set_ylabel(r"$\delta_{мд}, [мм]$", fontdict=font)
    force.set_ylabel(r"$P_{мд}, [даН]$", fontdict=font)

    axis.yaxis.label.set_color(p1.get_color())
    crimping.yaxis.label.set_color(p2.get_color())
    force.yaxis.label.set_color(p3.get_color())

    tkw = dict(size=5, width=1.5)
    axis.tick_params(axis='y', colors=p1.get_color(), **tkw)
    crimping.tick_params(axis='y', colors=p2.get_color(), **tkw)
    force.tick_params(axis='y', colors=p3.get_color(), **tkw)
    axis.tick_params(axis='x', **tkw)

    for ax in ['top', 'bottom', 'left', 'right']:
        axis.spines[ax].set_linewidth(1.5)

    force.vlines(value_p0, 0, straight_line_equation(value_p0, pressure_vals, force_vals),
                 color='g',
                 linewidth=2,
                 linestyle=':')

    force.hlines(straight_line_equation(value_p0, pressure_vals, force_vals), value_p0, force_vals[1],
                 color='g',
                 linewidth=2,
                 linestyle=':')

    crimping.vlines(value_p0, 0, straight_line_equation(value_p0, pressure_vals, crimping_vals),
                    color='r',
                    linewidth=2,
                    linestyle=':')

    crimping.hlines(straight_line_equation(value_p0, pressure_vals, crimping_vals), value_p0, crimping_vals[1],
                    color='r',
                    linewidth=2,
                    linestyle=':')

    axis.vlines(value_p0, 0, straight_line_equation(value_p0, pressure_vals, work_vals),
                color='b',
                linewidth=2,
                linestyle=':')

    axis.hlines(straight_line_equation(value_p0, pressure_vals, work_vals), 0, value_p0,
                color='b',
                linewidth=2,
                linestyle=':')

    # -------------------------------------------------------------------------------------------------------

    lines(axis, pressure_vals, work_vals, {"color": 'b',
                                           "linewidth": 1,
                                           "linestyle": (0, (5, 10))})

    lines(crimping, pressure_vals, crimping_vals, {"color": 'r',
                                                   "linewidth": 1,
                                                   "linestyle": (0, (5, 10))})

    lines(force, pressure_vals, force_vals, {"color": 'g',
                                             "linewidth": 1,
                                             "linestyle": (0, (5, 10))})

    output_data({
        'Aм.д. [даН * мм]': straight_line_equation(value_p0, pressure_vals, work_vals),
        'Delta_м.д. [мм]': straight_line_equation(value_p0, pressure_vals, crimping_vals),
        'Pм.д. [даН]': straight_line_equation(value_p0, pressure_vals, force_vals)})

    info_string = r"$A_{м.д.}$ = " + f"{round(straight_line_equation(value_p0, pressure_vals, work_vals), 2)} $[даН * мм]$\n" + \
                  r"$\delta_{м.д.}$ = " + f"{round(straight_line_equation(value_p0, pressure_vals, crimping_vals), 2)} $[мм]$\n" + \
                  r"$P_{м.д.}$ = " + f"{round(straight_line_equation(value_p0, pressure_vals, force_vals), 2)} $[даН]$\n" + \
                  r"$p_0$ = " + f"{round(value_p0, 2)} $[кгс/см^2]$\n"

    figure.text(0.45, 0.15, info_string, size=12, weight='bold')

    axis.legend(handles=[p1, p2, p3], loc='upper center', fontsize='x-large')

    axis.minorticks_on()
    axis.grid(which='major', color='#444', linewidth=0.5)
    axis.grid(which='minor', color='#aaa', ls=':')

    plt.show()
    log.info('График успешно построен')


def output_data(data):
    with open('result.yml', "w", encoding=ENCODING) as file:
        yaml.dump(data, file, allow_unicode=True, sort_keys=False)


def run(variant_number: int, amount_wheels: int):
    """
    Основной цикл программы

    Args:
        variant_number: номер варианта
        amount_wheels: кол-во колёс стойки

    """

    var_data = get_unique_variant(variant_number, input_data)
    pneumatic = pneumatics_selection(pneumatics_data, var_data, amount_wheels)

    log.info(var_data)

    if var_data is None:
        add_new_variant(variant_number, input_data)
        new_var_data = get_unique_variant(variant_number, input_data)

        print()
        for key, value in new_var_data.items():
            print(key, ':', value)

        print("\nПодобран пневматик:")

        for key, value in pneumatic.items():
            print(key, ':', value)

        plot(pneumatic, new_var_data["p0 * 10^5, [Па]"])

    else:

        log.info(pneumatic)

        print()
        for key, value in var_data.items():
            print(key, ':', value)

        print("\nПодобран пневматик:")

        for key, value in pneumatic.items():
            print(key, ':', value)

        plot(pneumatic, var_data["p0 * 10^5, [Па]"])


if __name__ == '__main__':
    # Инициализация входных данных:
    input_data = read_yml_file(Path('../data/variants_data.yml'))
    log.info('Входные данные успешно инициализированы')

    pneumatics_data = read_yml_file((Path('../data/pneumatics.yml')))

    run(int(input("Введите номер варианта: ")), int(input("Количество колёс у стойки шасси: ")))
