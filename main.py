import matplotlib.pyplot as plt
from pathlib import Path
from __log__ import log
import yaml

ENCODING = 'utf-8'
UNIT = 10


def cm_to_inch(value):
    return value/2.54


def get_parameter(value: float, coords_x: tuple, coords_y: tuple) -> float:
    return (coords_y[1] - coords_y[0]) * ((value - coords_x[0]) / (coords_x[1] - coords_x[0])) + coords_y[0]


def read_yml_file(path: Path):
    with open(path, "r", encoding=ENCODING) as file_data:
        return yaml.load(file_data, Loader=yaml.FullLoader)


def confirm_prompt(question: str) -> bool:
    answer = None
    while answer not in ("", "y", "ye", "yes", "n", "no"):
        answer = input(f"{question} [Y/n]: ").lower()
    return answer in ("", "y", "ye", "yes")


def str_into_tuple(string: str) -> tuple:
    return tuple(map(float, string.split(',')))


def upload_new_var_data(new_data: dict, variants_data: dict) -> None:
    variants_data['variants'].append(new_data)

    with open('variants_data.yml', "w", encoding=ENCODING) as file:
        yaml.dump(variants_data, file, allow_unicode=True, sort_keys=False)

        log.info('Входные данные успешно обновлены!')


def get_unique_variant(var_num: int, variants_data: dict) -> dict:
    for item in variants_data['variants']:
        if item.get('Номер варианта') == var_num:
            return item

    log.error(f'Вариант №{var_num} не найден!')


def add_new_variant(var_num: int, variants_data: dict):
    answer = confirm_prompt('\nWould you like to add data for this variant?')

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
    for item in pneumatics["pneumatics"]:
        if ((var_data['Pст.пос, [Н]'] / (UNIT * amount_wheels) < item["Pст.пос, [кгс]"]) &
            (var_data['Pст.взл, [Н]'] / (UNIT * amount_wheels) < item["Pст.взл, [кгс]"]) &
            (var_data['Vвзл, [км/ч]'] / amount_wheels < item["Vвзл, [км/ч]"]) &
            (var_data['Vпос, [км/ч]'] / amount_wheels < item["Vпос, [км/ч]"])) & \
                (str_into_tuple(item["p0, [кгс/см^2]"])[0] <= var_data["p0 * 10^5, [Па]"]
                 <= str_into_tuple(item["p0, [кгс/см^2]"])[1]):
            return item


def plot(data: dict, value: float):
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

    pressure_vals = str_into_tuple(data["p0, [кгс/см^2]"])
    work_vals = str_into_tuple(data["Aм.д, [кг*м]"])
    crimping_vals = str_into_tuple(data["delta_м.д, [мм]"])
    force_vals = str_into_tuple(data["Pм.д, [кгс]"])

    p1, = axis.plot(pressure_vals, work_vals, "b-", label="Максимально допустимая работа", linewidth=2)
    p2, = crimping.plot(pressure_vals, crimping_vals, "r-", label="Максимально допустимое обжатие", linewidth=2)
    p3, = force.plot(pressure_vals, force_vals, "g-", label="Максимально допустимая сила", linewidth=2)

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

    force.vlines(value, 0, get_parameter(value, pressure_vals, force_vals),
                 color='g',
                 linewidth=2,
                 linestyle=':')

    force.hlines(get_parameter(value, pressure_vals, force_vals), value, force_vals[1],
                 color='g',
                 linewidth=2,
                 linestyle=':')

    crimping.vlines(value, 0, get_parameter(value, pressure_vals, crimping_vals),
                    color='r',
                    linewidth=2,
                    linestyle=':')

    crimping.hlines(get_parameter(value, pressure_vals, crimping_vals), value, crimping_vals[1],
                    color='r',
                    linewidth=2,
                    linestyle=':')

    axis.vlines(value, 0, get_parameter(value, pressure_vals, work_vals),
                color='b',
                linewidth=2,
                linestyle=':')

    axis.hlines(get_parameter(value, pressure_vals, work_vals), 0, value,
                color='b',
                linewidth=2,
                linestyle=':')

    info_string = r"$A_{м.д.}$ = " + f"{round(get_parameter(value, pressure_vals, work_vals), 2)}, $[даН * мм]$\n" + \
                  r"$\delta_{м.д.}$ = " + f"{round(get_parameter(value, pressure_vals, crimping_vals), 2)}, $[мм]$\n" + \
                  r"$P_{м.д.}$ = " + f"{round(get_parameter(value, pressure_vals, force_vals), 2)}, $[даН]$\n" + \
                  r"$p_0$ = " + f"{round(value, 2)}, $[кгс/см^2]$\n"

    figure.text(0.45, 0.15, info_string, size=12, weight='bold')

    axis.legend(handles=[p1, p2, p3])
    # axis.grid()

    axis.minorticks_on()
    axis.grid(which='major', color='#444', linewidth=0.5)
    axis.grid(which='minor', color='#aaa', ls=':')

    # plt.savefig(f'{get_parameter(value, pressure_vals, work_vals)}.png')
    plt.show()
    log.info('График успешно построен')


def run(variant_number: int, amount_wheels: int):
    var_data = get_unique_variant(variant_number, input_data)

    # pprint(var_data)

    if var_data is None:
        add_new_variant(variant_number, input_data)
    else:
        # pprint(pneumatics_selection(pneumatics_data, var_data, amount_wheels))

        plot(pneumatics_selection(pneumatics_data, var_data, amount_wheels), var_data["p0 * 10^5, [Па]"])


if __name__ == '__main__':

    # Инициализация входных данных:
    input_data = read_yml_file(Path('variants_data.yml'))
    log.info('Входные данные успешно инициализированы')

    pneumatics_data = read_yml_file((Path('pneumatics.yml')))

    run(8, 2)
