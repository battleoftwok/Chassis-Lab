from __log__ import log
import yaml
import sys


def query_yes_no(question, default="yes"):

    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


with open('variants_data.yml', "r", encoding='windows-1251') as file_data:
    variants_data = yaml.load(file_data, Loader=yaml.FullLoader)

    log.info('Input data successfully initialized.')


def upload_new_data(new_data: dict):
    variants_data['data'].append(new_data)

    with open('variants_data.yml', "w") as file:
        yaml.dump(variants_data, file, allow_unicode=True, sort_keys=False)

        log.info('New data uploaded successfully!')


def get_unique_variant(var_num: int):
    for item in variants_data['data']:
        if item.get('Номер варианта') == var_num:
            return item

    log.error(f'Task variant №{var_num} not found!')


def add_new_variant(var_num: int):

    answer = query_yes_no('\nWould you like to add data for this variant?')

    if answer:
        upload_new_data({
            'Номер варианта': var_num,
            'Pст.пос, [Н]': int(input(f'\nPст.пос, [Н]: ')),
            'Pст.взл, [Н]': int(input(f'Pст.взл, [Н]: ')),
            'Aэ, [Дж]': int(input(f'Aэ, [Дж]: ')),
            'G0/Gпос, [-]': float(input(f'G0/Gпос, [-]: ')),
            'Vпос, [км / ч]': int(input(f'Vпос, [км / ч]: ')),
            'Vвзл, [км / ч]': int(input(f'Vвзл, [км / ч]: ')),
            'p0 * 10 ^ 5, [Па]': float(input(f'p0 * 10 ^ 5, [Па]: ')),
            'Индекс шасси': str(input(f'Индекс шасси: ')),
        })


def run(variant_number: int):

    var_data = get_unique_variant(variant_number)

    if var_data is None:
        add_new_variant(variant_number)
    else:
        print(var_data)


if __name__ == '__main__':

    run(1)
