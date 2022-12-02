from enum import Enum


# Лабораторная работа №3 по шасси (Майсак М.В.)


class ChassisType(Enum):
    main = "основная"
    nose = "носовая"


# =====================================================

# Тут менять данные:
input_data = {
    "Pст.пос., [Н]": 80000.0,  # см. входные данные
    "Pст.взл., [Н]": 112000.0,  # см. входные данные
    "n_y_max": 2.18,  # см. ЛР №2
    "Pм.д., [Н]": 86450.0,  # см. ЛР №1
    "𝛿_м.д., [мм]": 94.33,  # см. ЛР №1
    "Кол-во колёс": 4,
    "Вид стойки": "основная"  # или "носовая"
}

# =====================================================


def vertical_strike(landing_load: float, n_y_max: float) -> float:
    """
    Расчётная нагрузка при вертикальном ударе (посадка)

    Args:
            landing_load (float): статическая посадочная нагрузка (Pст.пос.)
            n_y_max (float): максимальная вертикальная перегрузка
    """

    f = 1.3

    return landing_load * n_y_max * f


def takeoff(takeoff_load: float) -> tuple:
    """
    Расчётная нагрузка при разбеге

    Args:
            takeoff_load (float): статическая взлётная нагрузка (Pст.взл.)
    """

    n_y_takeof = 2
    f = 1.5

    return takeoff_load * n_y_takeof * f, .3 * takeoff_load * n_y_takeof * f


def load_distribution(chassis_type: str, vert_strike_load: float) -> tuple:
    match ChassisType(chassis_type):
        case ChassisType.main:
            return .75 * vert_strike_load, .4 * vert_strike_load
        case ChassisType.nose:
            return vert_strike_load, .25 * vert_strike_load


def side_impact(vert_strike_load: float, wheels_amount: int, chassis_type: str):
    """
    Посадка с боковым ударом

    Args:
        vert_strike_load (float): [description]
        wheels_amount (int): [description] (default: `4`)
        chassis_type (str): [description] (default: `"основная"`)
    """
    loads = load_distribution(chassis_type, vert_strike_load)

    if wheels_amount == 1:
        return loads
    elif wheels_amount > 1 and wheels_amount % 2 == 0:
        return {"вся стойка": loads,
                "левое": (loads[0] * (.4 / (wheels_amount / 2)),
                          loads[1] * (.4 / (wheels_amount / 2))),
                "правое": ((loads[0] * (.6 / (wheels_amount / 2)),
                            loads[1] * (.6 / (wheels_amount / 2))))}
    else:
        raise ValueError("Может быть только чётное количество колёс!")


def chassis_compression(calc_load: tuple):
    """Обжатие
    
    Определение обжатия пневматика
    
    Args:
        calc_load (tuple): нагрузка при посадке с боковым ударом (Py_лев, Py_прав)

    """
    for load in calc_load:
        yield (load / 1.5) * (input_data["𝛿_м.д., [мм]"] / input_data["Pм.д., [Н]"])


if __name__ == '__main__':

    print(f"Входные данные варианта: \n")

    for i, j in input_data.items():
        print(f"{i} = {j}")

    print("\n1. Расчётные случаи:\n")

    print("a. Расчётная нагрузка при вертикальном ударе (посадка):")
    a = vertical_strike(input_data["Pст.пос., [Н]"], input_data["n_y_max"])
    b = takeoff(input_data["Pст.взл., [Н]"])

    print(f"Py(Eпос) = {a} [Н]")

    print("\nb. Расчётная нагрузка при разбеге:")
    print(f"(Py(Eвзл), Px(Eвзл)) = {b} [Н]")

    c = side_impact(a, input_data["Кол-во колёс"], input_data["Вид стойки"])

    print("\nc. Посадка с боковым ударом:")

    if input_data["Кол-во колёс"] == 1:
        print(f"(Py, Pz) = {c}")
        print("\n2. Определение обжатия пневматика:")
        print(f"𝛿_пн = {list(chassis_compression((c[0],)))}")

    else:
        print(f"Вся стойка: (Py, Pz) = {c['вся стойка']}")
        print(f"Левое колесо: (Py, Pz) = {c['левое']}")
        print(f"Правое колесо: (Py, Pz) = {c['правое']}")

        print("\n2. Определение обжатия пневматика:")
        print(f"(𝛿_пн.левое, 𝛿_пн.правое) = {tuple(chassis_compression((c['левое'][0], c['правое'][0])))}")
