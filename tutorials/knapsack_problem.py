from itertools import combinations
from typing import List

from dessia_common.core import PhysicalObject, DessiaObject


class Item(PhysicalObject):
    _standalone_in_db = True

    def __init__(self, mass: float, price: float, name: str = ''):
        self.mass = mass
        self.price = price
        PhysicalObject.__init__(self, name=name)

        self.price_per_kg = price / mass
        if self.price_per_kg <= 5:
            self.color = 'bronze'
            self.rgb = (97/255, 78/255, 26/255)  # Bronze color
        elif 5 < self.price_per_kg < 15:
            self.color = 'silver'
            self.rgb = (192/255, 192/255, 192/255)  # Silver color
        else:
            self.color = 'gold'
            self.rgb = (255/255, 215/255, 0/255)  # Gold color


class Knapsack(PhysicalObject):
    _standalone_in_db = True

    def __init__(self, allowed_mass: float, name: str = ''):
        self.allowed_mass = allowed_mass
        PhysicalObject.__init__(self, name=name)


class KnapsackPackage(Knapsack):
    _standalone_in_db = True

    def __init__(self, items: List[Item], allowed_mass: float, name: str):
        self.items = items
        Knapsack.__init__(self, allowed_mass=allowed_mass, name=name)

        self.mass = sum(item.mass for item in items)
        self.price = sum(item.price for item in items)
        self.golds = 0
        self.silvers = 0
        self.bronzes = 0
        for item in items:
            if item.color == 'gold':
                self.golds += 1
            elif item.color == 'silver':
                self.silvers += 1
            elif item.color == 'bronze':
                self.bronzes += 1


class Generator(DessiaObject):
    _standalone_in_db = True

    def __init__(self, items: List[Item], knapsack: Knapsack,
                 name: str = 'generator'):
        self.items = items
        self.knapsack = knapsack
        DessiaObject.__init__(self, name=name)

    def generate(self, min_mass: float, max_gold: int = None,
                 max_iter: int = None):
        solutions = []
        count = 0
        for i in range(1, len(self.items)+1):
            for combination in combinations(self.items, i):
                solution = KnapsackPackage(
                    items=combination,
                    allowed_mass=self.knapsack.allowed_mass,
                    name=f'Package {i}')

                if min_mass <= solution.mass <= self.knapsack.allowed_mass:
                    if max_gold is not None:
                        if solution.golds <= max_gold:
                            solutions.append(solution)
                            count += 1
                    else:
                        solutions.append(solution)
                        count += 1

                if max_iter is not None and count == max_iter:
                    return solutions

        return solutions
