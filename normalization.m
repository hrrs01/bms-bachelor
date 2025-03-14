% Load your test data (replace with your actual data loading)
close all; clc; clear;

rawdata = readtable("Battery Bachelor Testdata/Heimir/Cycle Testing of P28B cell1/Cycle Testing of P28B cell1.csv");
% trim first line as it is always garbage for some reason
rawdata = rawdata(2:end, :);

% A zero state hysteris model is used, following the form
% S_(k+1) = S_k - ((n_k*delta(t))/C_n)*I_k + omega_k
% U_k = K_0 - K_1/S_k - K_2 * S_k + K_3*ln(S_k) + K_4*ln(1-S_k) - R*I_k - h_k*H + v_k
% h_k = {1, I_k > epsilon; -1, I_k < -epsilon; h_k-1, abs(I_k) <= epsilon}

epsilon = 0.001;

U = rawdata.Voltage';
I = rawdata.Current';
t = seconds(rawdata.TotalTime)';

expected_capacity = 2650;

voltage = U; % Example: Voltage data in the first column
current = I; % Example: Current data in the second column
time = t;    % Example: Time data in the third column

% Estimate Battery Capacity (replace with your method)
% For example, integrate current over a full discharge cycle.
dt = diff(time);
capacity = sum(current(1:end-1) .* dt) / 360 / expected_capacity; % Rough estimate in Amp Hours

% Coulomb Counting
charge_change = current(1:end-1) .* dt; % Charge change in each interval (Amp-seconds)
total_charge = cumsum(charge_change); % Cumulative charge (Amp-seconds)

% Normalize SOC
soc = total_charge / (capacity * expected_capacity); % Assuming capacity is in Ah, convert to Amp-seconds

% Shift SOC to start from 0
soc = soc - min(soc);

% Flip it
soc = max(soc) - soc;

% Normalize the soc with the expected nominal capacity
soc = soc + expected_capacity - max(soc) - 0.01; % - 0.01 to make sure we are not at 100 soc for the model

% Normalize between 0 and 1, based on state of charge
soc = soc / expected_capacity;


% Plot Voltage vs SOC
figure;
plot(soc, voltage(2:end)); % Adjust voltage vector to match SOC length
xlabel('State of Charge (SOC)');
ylabel('Voltage (V)');
title('Voltage vs. State of Charge');
grid on;

% Data for model parameterization

timeline = time(2:end);
voltage = voltage(2:end);
current = -current(2:end); % For this model, discharge is positive and vice versa
soc = soc;
epsilon = 0.001;

M = zeros(length(soc), 8);

for idx=1:length(soc)
    M(idx,1) = 1;
    M(idx,2) = -(1/soc(idx));
    M(idx,3) = -soc(idx);
    M(idx,4) = log(soc(idx));
    M(idx,5) = log(1-soc(idx));
    M(idx,6) = 0;
    M(idx,7) = 0;
    if current(idx) < 0
        M(idx, 7) = -current(idx);
    else
        M(idx, 6) = -current(idx);
    end
    hk = 0;
    if current(idx) > epsilon
        hk = 1;
    elseif current(idx) < -epsilon
        hk = -1;
    else
        if idx>1
            hk = M(idx-1, 8);
        else
            hk = 1;
        end
    end
    M(idx,8) = -hk;
    
end

c = inv(M'*M)*M'*voltage';

soc_test = 0.20:0.01:0.99;

Uocv = c(1) - c(2)./soc_test - soc_test*c(3) + c(4)*log(soc_test) + c(5) * log(1 - soc_test);
Uout = Uocv - c(6) * 10 - c(8);
Uin = Uocv - c(7) * -10 + c(8);
hold on
plot(soc_test, Uocv, "Color", "red", "LineWidth", 2);
plot(soc_test, Uin, "Color", "blue", "LineWidth", 2);
plot(soc_test, Uout, "Color", "green", "LineWidth", 2);