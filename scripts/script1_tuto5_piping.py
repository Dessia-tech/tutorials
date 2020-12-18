import tutorials.tutorial5_piping as tuto
import plot_data.core as plot_data
import volmdlr as vm

f1 = vm.Frame3D(vm.Point3D(0.05, 0.1, 0), vm.Vector3D(1, 0, 0), vm.Vector3D(0, 1, 0), vm.Vector3D(0, 0, 1))
p1 = vm.faces.Plane3D(f1)
s1 = vm.faces.Surface2D(outer_contour=vm.wires.ClosedPolygon2D([vm.Point2D(-0.05, -0.1),
                                                                vm.Point2D(0.05, -0.1),
                                                                vm.Point2D(0.05, 0.1),
                                                                vm.Point2D(-0.05, 0.1)]),
                        inner_contours=[])
face1 = vm.faces.PlaneFace3D(surface3d=p1, surface2d=s1)


f2 = vm.Frame3D(vm.Point3D(0.05, 0.1, 0.005), vm.Vector3D(1, 0, 0), vm.Vector3D(0, 0, 1), vm.Vector3D(0, 1, 0))
p2 = vm.faces.Plane3D(f2)
s2 = vm.faces.Surface2D(outer_contour=vm.wires.ClosedPolygon2D([vm.Point2D(-0.05, -0.005),
                                                                vm.Point2D(0.05, -0.005),
                                                                vm.Point2D(0.05, 0.005),
                                                                vm.Point2D(-0.05, 0.005)]),
                        inner_contours=[])
face2 = vm.faces.PlaneFace3D(surface3d=p2, surface2d=s2)

vol = vm.core.VolumeModel([face1, face2])
# vol.babylonjs()

housing = tuto.Housing(faces=[face1, face2], origin=vm.Point3D(0, 0, 0))
# housing.babylonjs()

p1 = vm.Point3D(0, 0.1, 0.01)
p2 = vm.Point3D(0.05, 0.1, 0.01)
frame1 = tuto.Frame(start = p1, end = p2)

p1 = vm.Point3D(0.05, 0.1, 0.01)
p2 = vm.Point3D(0.1, 0.1, 0.01)
frame2 = tuto.Frame(start = p1, end = p2)

p1 = vm.Point3D(0, 0.2, 0)
p2 = vm.Point3D(0.05, 0.2, 0)
frame3 = tuto.Frame(start = p1, end = p2)

p1 = vm.Point3D(0.05, 0.2, 0)
p2 = vm.Point3D(0.1, 0.2, 0)
frame4 = tuto.Frame(start = p1, end = p2)

p1 = vm.Point3D(0, 0, 0)
p2 = vm.Point3D(0.1, 0, 0)
piping1 = tuto.Piping(start=p1, end=p2,
                      direction_start=vm.Vector3D(0, 0, 1), direction_end=vm.Vector3D(1, 0, 1),
                      diameter=0.005, length_connector=0.1, minimum_radius=0.03)
piping2 = tuto.Piping(start=p1, end=p2,
                      direction_start=vm.Vector3D(0, 0, 1), direction_end=vm.Vector3D(1, 0, 1),
                      diameter=0.005, length_connector=0.1, minimum_radius=0.05)

assembly1 = tuto.Assembly(frames=[frame1, frame3, frame4, frame2], piping=piping1, housing=housing)
assembly2 = tuto.Assembly(frames=[frame1, frame3, frame4, frame2], piping=piping2, housing=housing)
# assembly1.babylonjs()

opti1 = tuto.Optimizer()
solutions = opti1.optimize(assemblies=[assembly1, assembly2], number_solution_per_assembly=2)

for solution in solutions:
    solution.babylonjs()

primitives = solutions[0].volmdlr_primitives()
model = vm.core.VolumeModel(primitives)
model.to_step()
