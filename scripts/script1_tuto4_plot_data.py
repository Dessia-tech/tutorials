import tutorials.tutorial4_plot_data as tuto
import plot_data.core as plot_data
import volmdlr as vm

g1 = tuto.Graph(2, 50)

pdt = g1.plot_data()
plot_data.plot_canvas(plot_data_object=pdt, canvas_id='canvas',
                      debug_mode=True)

s1 = tuto.ScatterPlot()
plot_data.plot_canvas(plot_data_object=s1.plot_data(), canvas_id='canvas',
                      debug_mode=True)

from dessia_api_client import Client
c = Client(api_url='https://api.demo.dessia.tech')
r = c.create_object_from_python_object(g1)