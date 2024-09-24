import tutorials.tutorial7_update as tuto
import volmdlr as vm

c1 = tuto.Component(vm.Point2D(0,0), vm.Point2D(0,1), vm.Point2D(1,0), vm.Point2D(1,1))
opt1 = tuto.Optimizer(component=c1)
sol = opt1.optimize()