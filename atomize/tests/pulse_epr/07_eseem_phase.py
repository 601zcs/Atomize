import time
import datetime
import numpy as np
import atomize.general_modules.general_functions as general
import atomize.device_modules.PB_ESR_500_pro as pb_pro
import atomize.device_modules.Keysight_3000_Xseries as key
import atomize.device_modules.Mikran_X_band_MW_bridge as mwBridge
import atomize.device_modules.BH_15 as bh
import atomize.device_modules.SR_PTC_10 as sr
import atomize.general_modules.csv_opener_saver_tk_kinter as openfile

### Experimental parameters
POINTS = 400
STEP = 10                  # in NS; delta_start = str(STEP) + ' ns' -> delta_start = '10 ns'
FIELD = 3507
AVERAGES = 5

cycle_data_x = []
cycle_data_y = []
data_x = np.zeros(POINTS)
data_y = np.zeros(POINTS)
x_axis = np.arange(0, POINTS*STEP, STEP)
###

# initialization of the devices
file_handler = openfile.Saver_Opener()
ptc10 = sr.SR_PTC_10()
mw = mwBridge.Mikran_X_band_MW_bridge()
pb = pb_pro.PB_ESR_500_Pro()
t3034 = key.Keysight_3000_Xseries()
bh15 = bh.BH_15()

bh15.magnet_setup(FIELD, 1)
bh15.magnet_field(FIELD)

t3034.oscilloscope_trigger_channel('CH1')
t3034.oscilloscope_record_length(250)
t3034.oscilloscope_acquisition_type('Average')
t3034.oscilloscope_number_of_averages(AVERAGES)
t3034.oscilloscope_stop()

pb.pulser_pulse(name = 'P0', channel = 'MW', start = '100 ns', length = '16 ns', phase_list = ['+x', '-x', '+x', '-x'])
# 208 ns between P0 and P1 is set according to modulation deep in ESEEM. Can be adjust using different delays;
# thin acquisition window
pb.pulser_pulse(name = 'P1', channel = 'MW', start = '400 ns', length = '16 ns', phase_list = ['+x', '+x', '-x', '-x'])
pb.pulser_pulse(name = 'P2', channel = 'MW', start = '456 ns', length = '16 ns', delta_start = str(STEP) + ' ns', phase_list = ['+x', '+x', '+x', '+x'])
pb.pulser_pulse(name = 'P3', channel = 'TRIGGER', start = '756 ns', length = '100 ns', delta_start = str(STEP) + ' ns')

pb.pulser_repetitoin_rate('200 Hz')

for i in range(POINTS):

    # phase cycle
    j = 0
    while j < 4:

        pb.pulser_next_phase()

        t3034.oscilloscope_start_acquisition()
        area_x = t3034.oscilloscope_area('CH4')
        area_y = t3034.oscilloscope_area('CH3')

        cycle_data_x.append(area_x)
        cycle_data_y.append(area_y)

        j += 1
    
    # acquisition cycle [+, -, -, +]
    data_x[i] = (cycle_data_x[0] - cycle_data_x[1] - cycle_data_x[2] + cycle_data_x[3])/4
    data_y[i] = (cycle_data_y[0] - cycle_data_y[1] - cycle_data_y[2] + cycle_data_y[3])/4

    general.plot_1d('ESEEM', x_axis, data_x, xname = 'Delay',\
        xscale = 'ns', yname = 'Area', yscale = 'V*s', timeaxis = 'False', label = 'X')
    general.plot_1d('ESEEM', x_axis, data_y, xname = 'Delay',\
        xscale = 'ns', yname = 'Area', yscale = 'V*s', timeaxis = 'False', label = 'Y')

    pb.pulser_shift()

    cycle_data_x = []
    cycle_data_y = []

# Data saving
header = 'Date: ' + str(datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")) + '\n' + 'ESEEM\n' + \
            'Field: ' + str(FIELD) + ' G \n' + str(mw.mw_bridge_att_prm()) + '\n' + \
            str(mw.mw_bridge_synthesizer()) + '\n' + \
           'Repetition Rate: ' + str(pb.pulser_repetitoin_rate()) + '\n' +\
           'Averages: ' + str(AVERAGES) + '\n' + 'Window: ' + str(t3034.oscilloscope_timebase()*1000) + ' ns\n' + \
           'Temperature: ' + str(ptc10.tc_temperature('2A')) + ' K\n' +\
           'Pulse List: ' + '\n' + str(pb.pulser_pulse_list()) + 'Time (trig. delta_start), X (V*s), Y (V*s) '

file_handler.save_1D_dialog( (x_axis, data_x, data_y), header = header )

pb.pulser_stop()

