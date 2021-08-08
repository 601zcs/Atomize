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
POINTS = 194
STEP = 2                  # in NS; length incremen = str(STEP) + ' ns' -> length incremen = '2 ns'
FIELD = 3473
AVERAGES = 1000

# PULSES
REP_RATE = '500 Hz'
PULSE_1_LENGTH = '10 ns'
PULSE_2_LENGTH = '50 ns'
PULSE_3_LENGTH = '100 ns'
PULSE_1_START = '100 ns'
PULSE_2_START = '600 ns'
PULSE_3_START = '950 ns'
PULSE_SIGNAL_START = '1300 ns'

#
data_x = np.zeros(POINTS)
data_y = np.zeros(POINTS)
x_axis = np.arange(10, POINTS*STEP + 10, STEP) # 10 is initial length of the pulse
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

pb.pulser_pulse(name = 'P0', channel = 'MW', start = PULSE_1_START, length = PULSE_1_LENGTH, length_increment = str(STEP) + ' ns')
pb.pulser_pulse(name = 'P1', channel = 'MW', start = PULSE_2_START, length = PULSE_2_LENGTH)
pb.pulser_pulse(name = 'P2', channel = 'MW', start = PULSE_3_START, length = PULSE_3_LENGTH)
pb.pulser_pulse(name = 'P3', channel = 'TRIGGER', start = PULSE_SIGNAL_START, length = '100 ns')

pb.pulser_repetition_rate( REP_RATE )

for i in range(POINTS):

    pb.pulser_update()

    t3034.oscilloscope_start_acquisition()
    area_x = t3034.oscilloscope_area('CH4')
    area_y = t3034.oscilloscope_area('CH3')

    data_x[i] = area_x
    data_y[i] = area_y

    general.plot_1d('Nutation', x_axis, data_x, xname = 'Delay',\
        xscale = 'ns', yname = 'Area', yscale = 'V*s', label = 'X')

    general.plot_1d('Nutation', x_axis, data_y, xname = 'Delay',\
        xscale = 'ns', yname = 'Area', yscale = 'V*s', label = 'Y')

    pb.pulser_increment()

pb.pulser_stop()

# Data saving
header = 'Date: ' + str(datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")) + '\n' + 'Nutation\n' + \
            'Field: ' + str(FIELD) + ' G \n' + str(mw.mw_bridge_att_prm()) + '\n' + \
            str(mw.mw_bridge_synthesizer()) + '\n' + \
           'Repetition Rate: ' + str(pb.pulser_repetition_rate()) + '\n' +\
           'Averages: ' + str(AVERAGES) + '\n' + 'Window: ' + str(t3034.oscilloscope_timebase()*1000) + ' ns\n' + \
           'Temperature: ' + str(ptc10.tc_temperature('2A')) + ' K\n' +\
           'Pulse List: ' + '\n' + str(pb.pulser_pulse_list()) + 'Time (pulse length_increment), X (V*s), Y (V*s) '

file_handler.save_1D_dialog( (x_axis, data_x, data_y), header = header )

