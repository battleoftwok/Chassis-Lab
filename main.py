from pprint import pprint
import matplotlib.pyplot as plt
from pathlib import Path
from __log__ import log
import yaml

ENCODING = 'utf-8'
UNIT = 10


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

        log.info('New data uploaded successfully!')


def get_unique_variant(var_num: int, variants_data: dict) -> dict:
    for item in variants_data['variants']:
        if item.get('Номер варианта') == var_num:
            return item

    log.error(f'Task variant №{var_num} not found!')


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


def plot(data: dict):
    figure, axis = plt.subplots()
    figure.subplots_adjust(right=0.75)

    crimping = axis.twinx()
    force = axis.twinx()

    force.spines.right.set_position(("axes", 1.2))

    pressure_vals = str_into_tuple(data["p0, [кгс/см^2]"])
    work_vals = str_into_tuple(data["Aм.д, [кг*м]"])
    crimping_vals = str_into_tuple(data["delta_м.д, [мм]"])
    force_vals = str_into_tuple(data["Pм.д, [кгс]"])

    p1, = axis.plot(pressure_vals, work_vals, "b-", label="Макс. доп. работа")
    p2, = crimping.plot(pressure_vals, crimping_vals, "r-", label="Макс. до. обжатие")
    p3, = force.plot(pressure_vals, force_vals, "g-", label="Макс. доп. сила")

    # axis.set_xlim(0, 20)
    # axis.set_ylim(0, 2000)
    # crimping.set_ylim(0, 106)
    # force.set_ylim(0, 20000)

    axis.set_xlabel("p0, [кгс/см^2]")
    axis.set_ylabel("Aмд, [даН * мм]")
    crimping.set_ylabel("δ_мд, [мм]")
    force.set_ylabel("Pмд, [даН]")

    axis.yaxis.label.set_color(p1.get_color())
    crimping.yaxis.label.set_color(p2.get_color())
    force.yaxis.label.set_color(p3.get_color())

    tkw = dict(size=4, width=1.5)
    axis.tick_params(axis='y', colors=p1.get_color(), **tkw)
    crimping.tick_params(axis='y', colors=p2.get_color(), **tkw)
    force.tick_params(axis='y', colors=p3.get_color(), **tkw)
    axis.tick_params(axis='x', **tkw)

    axis.legend(handles=[p1, p2, p3])
    axis.grid()

    plt.show()


def run(variant_number: int, amount_wheels: int):
    var_data = get_unique_variant(variant_number, input_data)

    pprint(var_data)

    if var_data is None:
        add_new_variant(variant_number, input_data)
    else:
        pprint(pneumatics_selection(pneumatics_data, var_data, amount_wheels))
        plot(pneumatics_selection(pneumatics_data, var_data, amount_wheels))


if __name__ == '__main__':
    # Инициализация входных данных:
    input_data = read_yml_file(Path('variants_data.yml'))
    log.info('Input data successfully initialized.')

    pneumatics_data = read_yml_file((Path('pneumatics.yml')))

    run(1, 2)
