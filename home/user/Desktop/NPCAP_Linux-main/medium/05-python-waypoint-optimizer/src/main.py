import argparse
import json
from visualize import plot
from optimizer import optimize_route
import numpy as np
import matplotlib.pyplot as plt

# Парсер с переменными пути к миссии, метода поиска пути
# и визуализация точек пути
parser = argparse.ArgumentParser()
parser.add_argument('--mission', required=True)
parser.add_argument('--method')
parser.add_argument('--visualize', action='store_true')
args = parser.parse_args()

# Список словарей
with open (args.mission, 'r', encoding='utf-8') as file:
    json = json.load(file)
waypoints = json['waypoints']

result = optimize_route(waypoints, args.method)
print(result)

# print(f"Улучшение: {result['improvement']:.1f}%")

if args.visualize:
    plot(waypoints)