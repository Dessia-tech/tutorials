import tutorials.tutorial4_plot_data as tuto
import plot_data.core as plot_data
import volmdlr as vm

# g1 = tuto.Graph(2, 50)
# pdt = g1.plot_data()
# plot_data.plot_canvas(plot_data_object=pdt, canvas_id='canvas')

# g2 = tuto.Graphs(2, 50)
# pdt = g2.plot_data()
# plot_data.plot_canvas(plot_data_object=pdt, canvas_id='canvas')

# s1 = tuto.ScatterPlot(2, 2)
# # print(s1)
# plot_data.plot_canvas(plot_data_object=s1.plot_data(), canvas_id='canvas')

# p1 = tuto.ParallelPlot(2, 2)
# plot_data.plot_canvas(plot_data_object=p1.plot_data(), canvas_id='canvas')

# m1 = tuto.MultiPlot(2, 2)
# plot_data.plot_canvas(plot_data_object=m1.plot_data(), canvas_id='canvas')

shape1 = tuto.SimpleShape(3, 2)
plot_data.plot_canvas(plot_data_object=shape1.plot_data(), canvas_id='canvas')


# s1 = tuto.ScatterPlot_list([0,1,2,3,4,5], [1,0,2,5,4,3])
# plot_data.plot_canvas(plot_data_object=s1.plot_data(), canvas_id='canvas')

# from dessia_api_client import Client
# c = Client(api_url='https://api.stelia.dessia.tech')
# r = c.create_object_from_python_object(g1)
# r = c.create_object_from_python_object(g2)
# r = c.create_object_from_python_object(s1)
# r = c.create_object_from_python_object(p1)
# r = c.create_object_from_python_object(m1)
# r = c.create_object_from_python_object(shape1)