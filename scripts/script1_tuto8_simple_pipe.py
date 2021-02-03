import tutorials.tutorial8_simple_pipe as tuto
import plot_data.core as plot_data
import volmdlr as vm
import networkx as nx

lx, ly = 0.5, 0.5
lz = 0.05
frame = vm.Frame3D(vm.Point3D(0, 0, 0), lx * vm.Vector3D(1, 0, 0), ly * vm.Vector3D(0, 1, 0), lz * vm.Vector3D(0, 0, 1))
block = vm.primitives3d.Block(frame)
faces = block.faces[0:-1]
housing = tuto.Housing(faces, vm.Point3D(0, 0, 0))

p0 = block.faces[-1].outer_contour3d.primitives[0].start
p1 = block.faces[-1].outer_contour3d.primitives[2].start
# for prim in block.faces[-1].outer_contour3d.primitives:
#     print(prim.start, prim.end)
frame1 = tuto.Frame(p0, p1)

p3 = faces[1].bounding_box.center
dir3 = faces[1].surface3d.frame.w
p4 = faces[2].bounding_box.center
dir4 = faces[2].surface3d.frame.w
piping1 = tuto.MasterPiping(start=p3, end=p4,
                            direction_start=-dir3, direction_end=dir4,
                            diameter=0.005, length_connector=0.03, minimum_radius=0.01)

p5 = faces[0].bounding_box.center
dir5 = faces[0].surface3d.frame.w
piping2 = tuto.SlavePiping(start=p5,
                            direction_start=dir5, piping_master=piping1,
                            diameter=0.005, length_connector=0.03, minimum_radius=0.01)

p6 = faces[3].bounding_box.center
dir6 = faces[3].surface3d.frame.w
piping3 = tuto.SlavePiping(start=p6,
                            direction_start=-dir6, piping_master=piping2,
                            diameter=0.005, length_connector=0.03, minimum_radius=0.01)

# vol = vm.core.VolumeModel(faces)
# vol.babylonjs()
as1 = tuto.Assembly(frame=frame1, pipings=[piping1, piping2, piping3],
                    housing=housing)
g = as1.graph()
list_piping = as1.analyze_graph(g)

# as1.update([0.3, 0.5, 0.5])
# as1.babylonjs()

opt1 = tuto.Optimizer(as1, objective_length=1.1)
sol = opt1.optimize()
opt1.assembly.babylonjs()
print('Optimum with length {} with an objective at {}'.format(opt1.assembly.length(), opt1.objective_length))

graph = as1.graph()
nx.draw(graph)