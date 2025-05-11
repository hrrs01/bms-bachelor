clear; clc; close all;

s = serialport("/dev/ttyACM0", 115200);

cell1 = readtable("Battery Bachelor Testdata/Heimir/Test/Cycle Testing Save 1/Cycle Testing of P28B cell1.csv");
% Throw first row, as its empty
cell1 = cell1(2:10700, :);

cell2 = readtable("Battery Bachelor Testdata/Heimir/Test/Cycle Testing Save 1/Cycle Testing of P28B cell2.csv");
% Throw first row, as its empty
cell2 = cell2(2:10700, :);

cell3 = readtable("Battery Bachelor Testdata/Heimir/Test/Cycle Testing Save 1/Cycle Testing of P28B cell3.csv");
% Throw first row, as its empty
cell3 = cell3(2:10700, :);

responses = zeros(length(cell1.TotalTime),14);


for k=1:length(cell1.TotalTime)
    cell_voltages = typecast([(uint16(cell1.Voltage(k)*10000)), (uint16(cell2.Voltage(k)*10000)), (uint16(cell3.Voltage(k)*10000))], 'uint8');
    cell_temperatures = typecast([(uint16(cell1.T1(k)*10)),(uint16(cell2.T1(k)*10)),(uint16(cell3.T1(k)*10))], 'uint8');
    current = mean([cell1.Current(k), cell2.Current(k), cell3.Current(k)])*100;
    current = typecast((uint16(current)),'uint8');
    timestamp = typecast((uint32(milliseconds(cell1.TotalTime(k)))),'uint8');
    raw_timestamp = uint32(milliseconds(cell1.TotalTime(k)));
    padding = [uint8(0), uint8(0)];
    send_data = [cell_voltages, cell_temperatures, current,padding,timestamp];
    write(s, send_data, "uint8");

    response = read(s, 14, "uint8");

    responses(k, :) = response;

end

