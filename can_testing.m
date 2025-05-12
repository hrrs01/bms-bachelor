clear; close all; clc;

% Load test data
cell1 = readtable("Battery Bachelor Testdata/Heimir/Test/Cycle Testing Save 1/Cycle Testing of P28B cell1.csv");
% Throw first row, as its empty
cell1 = cell1(2:10700, :);

cell2 = readtable("Battery Bachelor Testdata/Heimir/Test/Cycle Testing Save 1/Cycle Testing of P28B cell2.csv");
% Throw first row, as its empty
cell2 = cell2(2:10700, :);

cell3 = readtable("Battery Bachelor Testdata/Heimir/Test/Cycle Testing Save 1/Cycle Testing of P28B cell3.csv");
% Throw first row, as its empty
cell3 = cell3(2:10700, :);

% Connect to CAN
can_channel = canChannel('SocketCAN', 'can0');
% Apply filters
filterAllowOnly(can_channel, [551, 583, 1031], 'Standard')
start(can_channel);

%% Section Transmit

capacities = zeros(length(cell1.TotalTime),3);
cell_socs = zeros(length(cell1.TotalTime),3);
pack_soc = zeros(length(cell1.TotalTime),1);

for k=1:length(cell1.TotalTime)
    message1 = canMessage(1063, false, 8);
    message2 = canMessage(1095, false, 8);
    if k == 1
        dt = cell1.TotalTime(k);
    else
        dt = cell1.TotalTime(k) - cell1.TotalTime(k-1);
    end
    pack(message1,uint16(milliseconds(dt)), 0, 16, 'LittleEndian');
    pack(message1,uint16(cell1.Voltage(k)*10000), 16, 16, 'LittleEndian');
    pack(message1,uint16(cell2.Voltage(k)*10000), 32, 16, 'LittleEndian');
    pack(message1,uint16(cell3.Voltage(k)*10000), 48, 16, 'LittleEndian');
    current = mean([cell1.Current(k), cell2.Current(k), cell3.Current(k)]);

    pack(message2,uint16(cell1.T1(k)*10), 0, 16, 'LittleEndian');
    pack(message2,uint16(cell2.T1(k)*10), 16, 16, 'LittleEndian');
    pack(message2,uint16(cell3.T1(k)*10), 32, 16, 'LittleEndian');
    pack(message2,int16(current*100), 48, 16, 'LittleEndian');
    got_ack = false;

    transmit(can_channel, message1);
    transmit(can_channel, message2);
    
    response = receive(can_channel, 2);
    for y=1:length(response)
        if response(y).ID == 551
            capacities(k,1) = unpack(response(y), 0, 16, 'LittleEndian', 'uint16');
            capacities(k,2) = unpack(response(y), 16, 16, 'LittleEndian', 'uint16');
            capacities(k,3) = unpack(response(y), 32, 16, 'LittleEndian', 'uint16');
        elseif response(y).ID == 583
            cell_socs(k,1) = unpack(response(y), 0, 16, 'LittleEndian', 'uint16');
            cell_socs(k,2) = unpack(response(y), 16, 16, 'LittleEndian', 'uint16');
            cell_socs(k,3) = unpack(response(y), 32, 16, 'LittleEndian', 'uint16');
            pack_soc(k) = unpack(response(y), 48, 16, 'LittleEndian', 'uint16');
        end
    end
    
end
%% View results

% Change DOD to SOC
discharge_idx = cell1.Current < 0;
cell1.SOC_DOD(discharge_idx) = 100 - cell1.SOC_DOD(discharge_idx);
plot(cell1.TotalTime, cell_socs(:,1));
hold on

plot(cell1.TotalTime, cell1.SOC_DOD);