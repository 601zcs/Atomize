import time
import numpy as np
from liveplot import LivePlotClient
import atomize.device_modules.config.messenger_socket_client as send

plotter = LivePlotClient()

xs=np.array([]);
ys=np.array([]);

# Plot_xy Test
for i in range(100):
	xs = np.append(xs, i);
	ys = np.append(ys, np.random.random_integers(0,10));
	plotter.plot_xy('Plot XY Test', xs, ys, label='test data')
	#time.sleep(0.1)

# Append_y Test
#xs = np.linspace(0, 39, 40)
#for val in np.sin(xs):
#    plotter.append_y('Append Y Test', val, start_step=(xs[0], xs[1]-xs[0]), label='test data')
#    time.sleep(0.1)

