from dessia_common.core import PhysicalObject, DessiaObject
from dessia_common.datatools.dataset import Dataset
from typing import List
from volmdlr.primitives3d import Block
from volmdlr import Frame3D, O3D, X3D, Y3D, Z3D


class Item(PhysicalObject):
    _standalone_in_db = True

    def __init__(self, mass: float, price: float, name: str):
        self.mass = mass
        self.price = price
        PhysicalObject.__init__(self, name=name)

    def volmdlr_primitives(self, z_offset: float = 0.):
        if self.price <= 10:
            color = (97/255, 78/255, 26/255)  # Bronze color
        elif 10 < self.price <= 25:
            color = (192/255, 192/255, 192/255)  # Silver color
        else:
            color = (255/255, 215/255, 0/255)  # Gold color
        height_vector = self.mass * Z3D / 2
        frame = Frame3D(origin=O3D + height_vector / 2 + z_offset * Z3D,
                        u=X3D,
                        v=Y3D,
                        w=height_vector,
                        name='frame ' + self.name)
        primitives = [Block(frame=frame,
                            color=color,
                            name='block ' + self.name)]
        return primitives


class Knapsack(PhysicalObject):
    _standalone_in_db = True

    def __init__(self, allowed_mass: float, name: str):
        self.allowed_mass = allowed_mass
        PhysicalObject.__init__(self, name=name)

    def volmdlr_primitives(self):
        height_vector = self.allowed_mass * Z3D / 2
        frame = Frame3D(origin=O3D + height_vector / 2,
                        u=1.1 * X3D,
                        v=1.1 * Y3D,
                        w=height_vector + 0.1 * Z3D,
                        name='frame ' + self.name)
        primitives = [Block(frame=frame,
                            alpha=0.3,
                            name='block ' + self.name)]
        return primitives


class KnapsackPackage(Knapsack):
    _vector_features = ["mass", "price"]
    _standalone_in_db = True

    def __init__(self, items: List[Item], allowed_mass: float, name: str):
        self.items = items
        self.mass = sum(item.mass for item in items)
        self.price = sum(item.price for item in items)
        Knapsack.__init__(self, allowed_mass=allowed_mass, name=name)

    def volmdlr_primitives(self):
        primitives = super().volmdlr_primitives()
        z_offset = 0
        for item in self.items:
            item_primitives = item.volmdlr_primitives(z_offset=z_offset)
            primitives.extend(item_primitives)
            z_offset += item.mass / 2
        return primitives


class Results(Dataset):

    def __init__(self, knapsack_packages: List[KnapsackPackage], name: str):
        self.knapsack_packages = knapsack_packages
        Dataset.__init__(self, dessia_objects=knapsack_packages, name=name)


class Generator(DessiaObject):
    _standalone_in_db = True

    def __init__(self, items: List[Item], knapsack: Knapsack):
        self.items = items
        self.knapsack = knapsack
        DessiaObject.__init__(self, name='generator')

    def generate(self, maximum: int = None):
        solutions = []
        for i in range(2**len(self.items)):

            if maximum is not None and i == maximum:
                break

            binary = format(i, 'b')

            selected_items = []
            selected_mass = 0
            for j in range(len(binary)):
                if binary[j] == '1':
                    selected_item = self.items[j]
                    selected_items.append(selected_item)
                    selected_mass += selected_item.mass

            if selected_mass <= self.knapsack.allowed_mass:
                solution = KnapsackPackage(
                    items=selected_items,
                    allowed_mass=self.knapsack.allowed_mass,
                    name=f'Package {i}')
                solutions.append(solution)

        return Results(knapsack_packages=solutions, name='results')
