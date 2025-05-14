clear; close all; clc;

rawdata = readtable("../previous_data/Heimir/Test/Cycle Testing Save 5/Cycle Testing of P28B Cell1 Save5.csv");
rawdata = rawdata(2:end, :);

non_pulse_idx = rawdata.StepType ~= "Pulse";

non_pulse_data = rawdata(non_pulse_idx, :);
dc_idx = non_pulse_data.Current < 0;
non_pulse_data.SOC_DOD(dc_idx) = 100-non_pulse_data.SOC_DOD(dc_idx);

plot(non_pulse_data.TotalTime, non_pulse_data.Voltage);
hold on
yyaxis right

plot(non_pulse_data.TotalTime, non_pulse_data.SOC_DOD);

