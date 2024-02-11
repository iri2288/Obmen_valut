import requests

INVALUTE = input('Введите валюту, которую Вы хотите поменять: ')
OUTVALUTE = input('Введите валюту, на которую вы хотите поменять: ')
INVALUTE_COUNT = float(input('Сколько Вы хотите поменять? : '))
get_str = f'http://127.0.0.1:8000/convert/?fv={INVALUTE}&sv={OUTVALUTE}&vcount={INVALUTE_COUNT}'
OUTVALUTE_COUNT = requests.get(get_str).json()
print(f'Клиенту нужно выдать {OUTVALUTE_COUNT} {OUTVALUTE}')