from __log__ import log
import yaml


ENCODING = 'utf-8'


with open('variants_data.yml', "r", encoding=ENCODING) as file_data:
    variants_data = yaml.load(file_data, Loader=yaml.FullLoader)

    log.info('Input data successfully initialized.')


def confirm_prompt(question: str) -> bool:
    answer = None
    while answer not in ("", "y", "ye", "yes", "n", "no"):
        answer = input(f"{question} [Y/n]: ").lower()
    return answer in ("", "y", "ye", "yes")


def upload_new_data(new_data: dict):
    variants_data['data'].append(new_data)

    with open('variants_data.yml', "w", encoding=ENCODING) as file:
        yaml.dump(variants_data, file, allow_unicode=True, sort_keys=False)

        log.info('New data uploaded successfully!')


def get_unique_variant(var_num: int):
    for item in variants_data['data']:
        if item.get('Номер варианта') == var_num:
            return item

    log.error(f'Task variant №{var_num} not found!')


def add_new_variant(var_num: int):

    answer = confirm_prompt('\nWould you like to add data for this variant?')

    if answer:
        upload_new_data({
            'Номер варианта': var_num,
            'Pст.пос, [Н]': int(input(f'\nPст.пос, [Н]: ')),
            'Pст.взл, [Н]': int(input(f'Pст.взл, [Н]: ')),
            'Aэ, [Дж]': int(input(f'Aэ, [Дж]: ')),
            'G0/Gпос, [-]': float(input(f'G0/Gпос, [-]: ')),
            'Vпос, [км/ч]': int(input(f'Vпос, [км/ч]: ')),
            'Vвзл, [км/ч]': int(input(f'Vвзл, [км/ч]: ')),
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

    # run(3)

    # t = tuple(int(item) for item in s.split(','))

    with open('pneumatics.yml', "r", encoding=ENCODING) as file_data:
        data = yaml.load(file_data, Loader=yaml.FullLoader)

    print(data)
