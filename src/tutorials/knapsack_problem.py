from __future__ import annotations
from itertools import combinations
from typing import ClassVar

from dessia_common.models.core import Model
from dessia_common.files import BinaryFile
from datatools.dataset import Dataset
from dessia_common.decorators import cad_view, plot_data_view, markdown_view
from dessia_common.models.decorators import modelclass, model_property
from plot_data import PrimitiveGroup, SurfaceStyle, Text, TextStyle
from plot_data.colors import BLACK, Color
from volmdlr import O3D, X3D, Y3D, Z3D, Frame3D, Point2D
from volmdlr.core import VolumeModel
from volmdlr.shapes import Solid
import volmdlr.step as vms
from volmdlr.wires import ClosedPolygon2D

from dessia_common.typings import KeyOf

ITEM_COLORS = {
    "bronze": (97/255, 78/255, 26/255),
    "silver": (192/255, 192/255, 192/255),
    "gold": (255/255, 215/255, 0/255)
}

ItemColor = KeyOf[ITEM_COLORS]

@modelclass
class Item(Model):
    """
    Class used to define an Item for Knapsack filling

    :param mass: Item mass in [kg]
    :param price: Item price
    """
    mass: float
    price: float

    _standalone_in_db: ClassVar[bool] = True

    @model_property
    def price_per_kg(self) -> float:
        return self.price / self.mass

    @model_property
    def color(self) -> ItemColor:
        if self.price_per_kg <= 5:
            return "bronze"
        if 5 < self.price_per_kg < 15:
            return "silver"
        return "gold"

    @model_property
    def rgb(self) -> tuple[float, float, float]:  # Would be awesome to compute type from constant values
        return ITEM_COLORS[self.color]

    def volmdlr_primitives(self, z_offset: float = 0., reference_path: str = "#", **kwargs):
        height_vector = self.mass * Z3D / 2
        frame = Frame3D(origin=O3D + height_vector / 2 + z_offset * Z3D,
                        u=X3D,
                        v=Y3D,
                        w=Z3D,
                        name=f"frame {self.name}")
        solid = Solid.make_box(length=1, width=1, height=height_vector.norm(), frame=frame,
                                     frame_centered=True, name=f"block {self.name}")
        solid.reference_path = reference_path
        solid.color = self.rgb
        return [solid]

    @cad_view("Item CAD")
    def cadview(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

    @plot_data_view("2D display for Item")
    def display_2d(self, y_offset: float = 0., reference_path: str = "#"):
        contour = ClosedPolygon2D([
            Point2D(-0.5, -0.5 + y_offset),
            Point2D(0.5, -0.5 + y_offset),
            Point2D(0.5, 0.5 + y_offset),
            Point2D(-0.5, 0.5 + y_offset)])
        contour.reference_path = reference_path
        surface_style = SurfaceStyle(color_fill=Color(red=self.rgb[0],green=self.rgb[1], blue=self.rgb[2]))
        primitive1 = contour.plot_data(surface_style=surface_style)
        text_style = TextStyle(text_color=BLACK,
                               font_size=None,
                               text_align_x="center",
                               text_align_y="middle")
        primitive2 = Text(comment=f"{self.mass} kg",
                          position_x=0,
                          position_y=0.4 + y_offset,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=0.5,
                          multi_lines=False)
        primitive3 = Text(comment=f"{self.price} €",
                          position_x=0,
                          position_y=-0.1 + y_offset,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=0.5,
                          multi_lines=False)
        return PrimitiveGroup(primitives=[primitive1, primitive2, primitive3])

@modelclass
class Item2(Model):
    """
    Class used to define an Item for Knapsack filling

    :param mass: Item mass in [kg]
    :param price: Item price
    """
    mass: float
    price: float
    variable: float

    _standalone_in_db: ClassVar[bool] = True

    @model_property
    def price_per_kg(self) -> float:
        return self.variable * self.price / self.mass

    @model_property
    def color_frame(self) -> ItemColor:
        if self.price_per_kg <= 5:
            return "bronze"
        if 5 < self.price_per_kg < 15:
            return "silver"
        return "gold"

    @model_property
    def rgb(self) -> tuple[float, float, float]:  # Would be awesome to compute type from constant values
        return ITEM_COLORS[self.color]

    def volmdlr_primitives(self, z_offset: float = 0., reference_path: str = "#", **kwargs):
        height_vector = self.price_per_kg * Z3D / 2
        frame = Frame3D(origin=O3D + height_vector / 2 + z_offset * Z3D,
                        u=X3D,
                        v=Y3D,
                        w=Z3D,
                        name=f"frame {self.name}")
        solid = Solid.make_box(length=1, width=1, height=height_vector.norm(), frame=frame,
                                     frame_centered=True, name=f"block {self.name}")
        solid.reference_path = reference_path
        solid.color = self.rgb
        return [solid]

    @cad_view("Item CAD")
    def cadview(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

    @plot_data_view("2D display for Item")
    def display_2d(self, y_offset: float = 0., reference_path: str = "#"):
        contour = ClosedPolygon2D([
            Point2D(-0.5, -0.5 + y_offset),
            Point2D(0.5, -0.5 + y_offset),
            Point2D(0.5, 0.5 + y_offset),
            Point2D(-0.5, 0.5 + y_offset)])
        contour.reference_path = reference_path
        surface_style = SurfaceStyle(color_fill=Color(red=self.rgb[0],green=self.rgb[1], blue=self.rgb[2]))
        primitive1 = contour.plot_data(surface_style=surface_style)
        text_style = TextStyle(text_color=BLACK,
                               font_size=None,
                               text_align_x="center",
                               text_align_y="middle")
        primitive2 = Text(comment=f"{self.mass} kg",
                          position_x=0,
                          position_y=0.4 + y_offset,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=0.5,
                          multi_lines=False)
        primitive3 = Text(comment=f"{self.price} €",
                          position_x=0,
                          position_y=-0.1 + y_offset,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=0.5,
                          multi_lines=False)
        return PrimitiveGroup(primitives=[primitive1, primitive2, primitive3])


@modelclass
class Items(Model):
    """
    Class used to define a list of Item for Knapsack filling.

    :param items: List of the items contained in the KnapsackPackage
    """
    items: list[Item]
    items2: list[Item2]

    _standalone_in_db: ClassVar[bool] = True

    def volmdlr_primitives(self, reference_path: str = "#", **kwargs):
        primitives = []
        z_offset = 0
        for i, item in enumerate(self.items):
            item_primitives = item.volmdlr_primitives(z_offset=z_offset, reference_path=f"{reference_path}/items/{i}")
            primitives.extend(item_primitives)
            z_offset += item.mass / 2 + 0.05
        for i, item in enumerate(self.items2):
            z_offset = - item.price_per_kg / 2 + 0.05
            item_primitives = item.volmdlr_primitives(z_offset=z_offset, reference_path=f"{reference_path}/items/{i}")
            primitives.extend(item_primitives)
        return primitives

    @cad_view("Knapsack CAD")
    def cadview(self, reference_path: str = "#"):
        return VolumeModel(self.volmdlr_primitives(reference_path=reference_path)).babylon_data()

    @plot_data_view("2D display for KnapsackPackage")
    def display_2d(self, reference_path: str = "#"):
        primitives = []
        y_offset = 0
        for i, item in enumerate(self.items):
            primitive_groups = item.display_2d(y_offset=y_offset)
            primitives.extend(primitive_groups.primitives)
            y_offset += 1.1

        return PrimitiveGroup(primitives=primitives)


@modelclass
class Knapsack(Model):
    """
    Class used to define a Knapsack and its filling capacity.
    This Knapsack class does not contain any item yet.

    :param allowed_mass: Mass capacity of the Knapsack in [kg]
    """
    allowed_mass: float
    name: str = ""

    _standalone_in_db = True

    def volmdlr_primitives(self):
        height_vector = (self.allowed_mass + 0.5) * Z3D / 2
        frame = Frame3D(origin=O3D + height_vector / 2,
                        u=X3D,
                        v=Y3D,
                        w=Z3D,
                        name=f"frame {self.name}")
        primitives = [Solid.make_box(length=1.1, width=1.1, height=height_vector.norm(), frame=frame,
                                     frame_centered=True, name=f"block {self.name}")]
        primitives[0].alpha = 0.4
        return primitives

    @classmethod
    def from_step_stream(cls, file_component: BinaryFile) -> Knapsack:
        """
        Method used to load a Knapsack in step format
        :param file_component: Knapsack defined from step file
        :return: Knapsack
        """
        file = vms.Step.from_stream(file_component)
        volume = file.to_volume_model()
        allowed_mass = 2 * (volume.primitives[0].bounding_box.size[2] - 0.1) - 0.5
        return cls(allowed_mass=allowed_mass)

    @cad_view("Knapsack CAD")
    def cadview(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

@modelclass
class KnapsackPackage(Knapsack):
    """
    Class used to define a Knapsack Package containing items.

    :param items: List of the items contained in the KnapsackPackage
    :param allowed_mass: Mass maximum capacity of the KnapsackPackage in [kg]
    """
    items: Items
    name: str = ""

    _standalone_in_db = True
    _vector_features = ["mass", "price", "golds", "silvers", "bronzes"]

    @model_property
    def mass(self) -> float:
        return sum(item.mass for item in self.items.items)

    @model_property
    def price(self) -> float:
        return sum(item.mass for item in self.items.items)

    @model_property
    def bronzes(self) -> int:
        return len([i for i in self.items.items if i.color == "bronze"])

    @model_property
    def silvers(self) -> int:
        return len([i for i in self.items.items if i.color == "silver"])

    @model_property
    def golds(self) -> int:
        return len([i for i in self.items.items if i.color == "gold"])

    def volmdlr_primitives(self):
        primitives = super().volmdlr_primitives()
        z_offset = 0
        for item in self.items.items:
            item_primitives = item.volmdlr_primitives(z_offset=z_offset)
            primitives.extend(item_primitives)
            z_offset += item.mass / 2 + 0.05
        return primitives

    @cad_view("Knapsack Package CAD")
    def cadview(self):
        return VolumeModel(self.volmdlr_primitives()).babylon_data()

    @plot_data_view("2D display for KnapsackPackage", picture=True)
    def display_2d(self):
        primitives = []
        y_offset = 0
        for item in self.items.items:
            primitive_groups = item.display_2d(y_offset=y_offset)
            primitives.extend(primitive_groups.primitives)
            y_offset += 1.1
        text_style = TextStyle(text_color=BLACK,
                               font_size=None,
                               text_align_x="center",
                               text_align_y="middle")
        primitive1 = Text(comment=f"{self.mass} kg",
                          position_x=0,
                          position_y=-1.5,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=1,
                          multi_lines=False)
        primitive2 = Text(comment=f"{self.price} €",
                          position_x=0,
                          position_y=-2,
                          text_style=text_style,
                          text_scaling=True,
                          max_width=1,
                          multi_lines=False)
        primitives.extend([primitive1, primitive2])
        return PrimitiveGroup(primitives=primitives)


@modelclass
class ListKnapsackPackages(Model):
    """
        Class used to store a list of solutions of Knapsack containing items.

        :param knapsack_packages: List of Knapsack solutions containing items

    """
    knapsack_packages: list[KnapsackPackage]
    name: str = "generator"

    _standalone_in_db = True

    @markdown_view("Generator markdown")
    def to_markdown(self, *args, **kwargs) -> str:
        """Render a markdown of the object output type: string."""
        dataset_object = Dataset(dessia_objects=self.knapsack_packages, name=self.name)
        return Dataset.to_markdown(dataset_object, *args, **kwargs)


@modelclass
class Generator(Model):
    """
    Class used to generate different solutions of Knapsack containing items.

    :param items: List of items available in the store for Knapsack filling
    :param knapsack: Knapsack to be filled with items
    """
    items: list[Item]
    knapsack: Knapsack
    name: str = "generator"

    _standalone_in_db = True

    def generate(self, min_mass: float, max_gold: int = None, max_iter: int = None):
        """
        Method for generation of filled Knapsack with restriction parameters for generation.

        :param min_mass: Minimal Mass of combined items to reach for a solution to be generated
        :param max_gold: Maximal number of gold items not to be exceeded for a solution to be generated
        :param max_iter: Maximum number of solutions generated (when the algorithm reaches this maximum iteration
            number, generation stops)

        :rtype: ListKnapsackPackages
        """
        solutions = []
        count = 0
        print(f"A list of {len(self.items)} items has been given as input. \n")
        print("Item combinations in Knapsack are created and compared to imposed filtering values.")
        for i in range(1, len(self.items) + 1):
            for combination in combinations(self.items, i):
                items_object = Items(items=combination)
                solution = KnapsackPackage(
                    items=items_object,
                    allowed_mass=self.knapsack.allowed_mass,
                    name=f"Package {i}"
                )
                count += 1

                if min_mass <= solution.mass <= self.knapsack.allowed_mass:
                    if max_gold is not None:
                        if solution.golds <= max_gold:
                            solutions.append(solution)
                    else:
                        solutions.append(solution)

                if max_iter is not None and count == max_iter:
                    print("The maximum number of iteration has been reached.")
                    print(f"Generation has been stopped and contains {len(solutions)} solutions")
                    return ListKnapsackPackages(
                        knapsack_packages=sorted(solutions, key=lambda x: x.price, reverse=True)
                    )

        print(f"Generation has been stopped and contains {len(solutions)} solutions")
        return ListKnapsackPackages(knapsack_packages=sorted(solutions, key=lambda x: x.price, reverse=True),
                                    name=self.name)

    def generate_knapsack_package(self) -> KnapsackPackage:
        """
        Method used to fill in a Knapsack with items

        :rtype: KnapsackPackage
        """

        sum_masses = sum(item.mass for item in self.items)
        while sum_masses > self.knapsack.allowed_mass:
            print("Too many items have been given at the input compared to the knapsack allowed mass.")
            print("The last item from the input list is removed.")
            self.items = self.items[0:(len(self.items)-1)]
            sum_masses = sum(item.mass for item in self.items)

        print(f"The knapsack finally contains {len(self.items)} items for global mass of {sum_masses} kg")
        items = Items(self.items)
        return KnapsackPackage(items=items, allowed_mass=self.knapsack.allowed_mass)
