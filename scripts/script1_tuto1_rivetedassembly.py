import tutorials.tutorial1_rivetedassembly as tuto
import plot_data.core as plot_data
import volmdlr as vm

p1 = tuto.Panel(1, 1, 0.01)
p2 = tuto.Panel(1.1, 1, 0.01)
# p1.babylonjs()

c = p1.plot_data()
plot_data.plot_canvas(c.to_dict(), canvas_id='canvas', debug_mode=False)

r1 = tuto.Rivet(0.01, 0.05, 0.012, 0.005)
# r1.babylonjs()

c = r1.plot_data(True)
plot_data.plot_canvas(c.to_dict(), canvas_id='canvas', debug_mode=False)

pc1 = tuto.PanelCombination([p1, p2], [vm.Point3D(0, 0, 0), vm.Point3D(0.7, 0.2, 0.01)])
sol = pc1.intersection_area()
c3 = sol.plot_data()
cs = pc1.plot_data()
primitives = plot_data.PrimitiveGroup(contours=[c3]+[cs[0], cs[1], cs[2]])
plot_data.plot_canvas(primitives.to_dict(), canvas_id='canvas', debug_mode=False)

rule1 = tuto.Rule(0.1, 0.2)
all_possibilities = rule1.define_number_rivet(sol, r1)

g1 = tuto.Generator(pc1, r1, rule1)
solutions = g1.generate()

cs = solutions[-1].plot_data()
plot_data.plot_canvas(cs.to_dict(), canvas_id='canvas', debug_mode=False)