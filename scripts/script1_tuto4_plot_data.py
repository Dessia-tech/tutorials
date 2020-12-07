import tutorials.tutorial4_plot_data as tuto
import plot_data.core as plot_data
import volmdlr as vm

g1 = tuto.Graph(2, 50)

pdt = g1.plot_data()
plot_data.plot_canvas(plot_data_object=pdt, canvas_id='canvas',
                      debug_mode=True)