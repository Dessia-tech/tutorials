from tutorials.knapsack_problem_with_displays import Item, Knapsack, Generator

items = [
    Item(mass=1, price=15, name='item 1'),
    Item(mass=2, price=35, name='item 2'),
    Item(mass=3, price=10, name='item 3'),
    Item(mass=1, price=30, name='item 4'),
    Item(mass=2, price=20, name='item 5'),
    Item(mass=3, price=25, name='item 6'),
    Item(mass=1, price=5, name='item 7'),
    Item(mass=2, price=10, name='item 8'),
    Item(mass=3, price=40, name='item 9')]

knapsack = Knapsack(allowed_mass=10, name='knapsack 10kg')

generator = Generator(items=items, knapsack=knapsack)
solutions = generator.generate(min_mass=5, max_gold=1)

solutions.sort(key=lambda x: x.price)
solutions[-1].display_2d().plot()
solutions[-1].babylonjs()
