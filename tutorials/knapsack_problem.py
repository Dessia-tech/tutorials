from itertools import combinations
from typing import List

from dessia_common.core import PhysicalObject, DessiaObject
from dessia_common.decorators import plot_data_view
from dessia_common.datatools import dataset

from plot_data import PrimitiveGroup, Text, TextStyle, SurfaceStyle
from volmdlr import Frame3D, O3D, X3D, Y3D, Z3D, Point2D
from volmdlr.primitives3d import Block
from volmdlr.wires import ClosedPolygon2D
from volmdlr.shapes import Solid
from dessia_common.displays import DisplaySetting

class Item(PhysicalObject):
    """
    Class used to define an Item for Knapsack filling

    :param mass: Item mass in [kg]
    :type mass: float

    :param price: Item price
    :type price: float
    """
    
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

    def volmdlr_primitives(self, z_offset: float = 0.):
        height_vector = self.mass * Z3D / 2
        frame = Frame3D(origin=O3D + height_vector / 2 + z_offset * Z3D,
                        u=X3D,
                        v=Y3D,
                        w=Z3D,
                        name='frame ' + self.name)
        primitives = [Solid.make_box(length=1, width=1, height=height_vector.norm(), frame=frame, frame_centered=True, name='block ' + self.name)]
        return primitives

    @plot_data_view("2D display for Item")
    def display_2d(self, y_offset: float = 0.):
        contour = ClosedPolygon2D([
            Point2D(-0.5, -0.5 + y_offset),
            Point2D(0.5, -0.5 + y_offset),
            Point2D(0.5, 0.5 + y_offset),
            Point2D(-0.5, 0.5 + y_offset)])
        surface_style = SurfaceStyle(
            color_fill=f'rgb({self.rgb[0]*255},{self.rgb[1]*255},{self.rgb[2]*255}')
        primitive1 = contour.plot_data(surface_style=surface_style)
        text_style = TextStyle(text_color='rgb(0, 0, 0)',
                               font_size=None,
                               text_align_x='center',
                               text_align_y='middle')
        primitive2 = Text(comment=f'{self.mass} kg',
                          position_x=0,
                          position_y=0.4 + y_offset,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=0.5,
                          multi_lines=False)
        primitive3 = Text(comment=f'{self.price} €',
                          position_x=0,
                          position_y=-0.1 + y_offset,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=0.5,
                          multi_lines=False)
        return PrimitiveGroup(primitives=[primitive1, primitive2, primitive3])


class Knapsack(PhysicalObject):
    """
    Class used to define a Knapsack and its filling capacity.
    This Knapsack class does not contain any item yet.

    :param allowed_mass: Mass capacity of the Knapsack in [kg]
    :type allowed_mass: float
    """
    
    _standalone_in_db = True

    def __init__(self, allowed_mass: float, name: str = ''):
        self.allowed_mass = allowed_mass
        PhysicalObject.__init__(self, name=name)

    def volmdlr_primitives(self):
        height_vector = (self.allowed_mass + 0.5) * Z3D / 2
        frame = Frame3D(origin=O3D + height_vector / 2,
                        u=X3D,
                        v=Y3D,
                        w=Z3D,
                        name='frame ' + self.name)
        primitives = [Solid.make_box(length=1.1, width=1.1, height=height_vector.norm(), frame=frame,frame_centered=True, name='block ' + self.name)]
        primitives[0].alpha = 0.4
        return primitives


class KnapsackPackage(Knapsack):
    """
    Class used to define a Knapsack Package containing items.

    :param items: List of the items contained in the KnapsackPackage
    :type items: List[Item]
    
    :param allowed_mass: Mass maximum capacity of the KnapsackPackage in [kg]
    :type allowed_mass: float
    """
    
    _standalone_in_db = True
    _vector_features = ['mass', 'price', 'golds', 'silvers', 'bronzes']

    def __init__(self, items: List[Item], allowed_mass: float, name: str = ''):
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

    def volmdlr_primitives(self):
        primitives = super().volmdlr_primitives()
        z_offset = 0
        for item in self.items:
            item_primitives = item.volmdlr_primitives(z_offset=z_offset)
            primitives.extend(item_primitives)
            z_offset += item.mass / 2 + 0.05
        return primitives

    @plot_data_view("2D display for KnapsackPackage")
    def display_2d(self):
        primitives = []
        y_offset = 0
        for item in self.items:
            primitive_groups = item.display_2d(y_offset=y_offset)
            primitives.extend(primitive_groups.primitives)
            y_offset += 1.1
        text_style = TextStyle(text_color='rgb(0, 0, 0)',
                               font_size=None,
                               text_align_x='center',
                               text_align_y='middle')
        primitive1 = Text(comment=f'{self.mass} kg',
                          position_x=0,
                          position_y=-1.5,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=1,
                          multi_lines=False)
        primitive2 = Text(comment=f'{self.price} €',
                          position_x=0,
                          position_y=-2,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=1,
                          multi_lines=False)
        primitives.extend([primitive1, primitive2])
        return PrimitiveGroup(primitives=primitives)

    @staticmethod
    def display_settings():
        """
        Returns a list of objects describing how to call subdisplays.
        """

        return [DisplaySetting(selector="2D display for KnapsackPackage", type_="plot_data",
                                method="display_2d", serialize_data=True, load_by_default=True)]

class ListKnapsackPackages(DessiaObject):
    """
        Class used to store a list of solutions of Knapsack containing items.

        :param knapsack_packages: List of Knapsack solutions containing items
        :type knapsack_packages: List[KnapsackPackage]

    """

    _standalone_in_db = True

    def __init__(self, knapsack_packages: List[KnapsackPackage], name: str = 'generator'):
        self.knapsack_packages = knapsack_packages
        DessiaObject.__init__(self, name=name)

    def to_markdown(self, *args, **kwargs) -> str:
        """Render a markdown of the object output type: string."""
        dataset_object = dataset.Dataset(dessia_objects=self.knapsack_packages)
        returned_markdown = dataset.Dataset.to_markdown(dataset_object, *args, **kwargs)
        return returned_markdown


class Generator(DessiaObject):
    """
    Class used to generate different solutions of Knapsack containing items.

    :param items: List of items available in the store for Knapsack filling
    :type items: List[Item]
    
    :param knapsack: Knapsack to be filled with items
    :type knapsack: Knapsack
    """
    
    _standalone_in_db = True

    def __init__(self, items: List[Item], knapsack: Knapsack, name: str = 'generator'):
        self.items = items
        self.knapsack = knapsack
        DessiaObject.__init__(self, name=name)

    def generate(self, min_mass: float, max_gold: int = None,
                 max_iter: int = None):
        """
        Method for generation of filled Knapsack with restriction parameters for generation.

        :param min_mass: Minimal Mass of combined items to reach for a solution to be generated
        :type min_mass: float

        :param max_gold: Maximal number of gold items not to be exceeded for a solution to be generated 
        :type max_gold: int

        :param max_iter: Maximum number of solutions generated (when the algorithm reaches this maximum iteration number, generation stops)
        :type max_iter: int
        
        :rtype: ListKnapsackPackages
        """
        solutions = []
        count = 0
        for i in range(1, len(self.items)+1):
            for combination in combinations(self.items, i):
                solution = KnapsackPackage(
                    items=combination,
                    allowed_mass=self.knapsack.allowed_mass,
                    name=f'Package {i}')
                count += 1

                if min_mass <= solution.mass <= self.knapsack.allowed_mass:
                    if max_gold is not None:
                        if solution.golds <= max_gold:
                            solutions.append(solution)
                    else:
                        solutions.append(solution)

                if max_iter is not None and count == max_iter:
                    return ListKnapsackPackages(
                        knapsack_packages=sorted(solutions,
                                                 key=lambda x: x.price,
                                                 reverse=True))

        return ListKnapsackPackages(knapsack_packages=sorted(solutions,
                                                             key=lambda x: x.price,
                                                             reverse=True))
