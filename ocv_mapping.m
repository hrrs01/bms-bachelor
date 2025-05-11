close all; clc; clear;

rawdata = readtable("Battery Bachelor Testdata/Heimir/Test/Cycle Testing Save 5/Cycle Testing of P28B Cell1 Save5.csv");
% trim first line as it is always garbage for some reason

idx = rawdata.CycleIndex > 1 & (rawdata.StepIndex == 2 | rawdata.StepIndex == 4) & (rawdata.Current > 0 | rawdata.Current < 0);


filtereddata = rawdata(idx, :);
rowsToChange = filtereddata.Current < 0;
filtereddata.SOC_DOD(rowsToChange) = 100 - filtereddata.SOC_DOD(rowsToChange);

time = filtereddata.TotalTime;


% plot(filtereddata.TotalTime, filtereddata.Voltage);
% hold on;
% plot(time, filtereddata.SOC_DOD)
% plot(filtereddata.TotalTime, filtereddata.Current);

plot(filtereddata.SOC_DOD, filtereddata.Voltage)
