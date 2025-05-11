% Load your test data (replace with your actual data loading)
close all; clc; clear;

rawdata = readtable("Battery Bachelor Testdata/Heimir/Cycle Testing of P28B cell1/Cycle Testing of P28B cell1.csv");
% trim first line as it is always garbage for some reason
chg1 = rawdata(5:2679, :); % thrown away since its not a full cycle and skews model
dchg1 = rawdata(2742:6178, :);
chg2 = rawdata(6184:9634, :);
dchg2 = rawdata(9697:13128, :);
pulse1 = rawdata(22038:23570, :);

% A zero state hysteris model is used, following the form
% S_(k+1) = S_k - ((n_k*delta(t))/C_n)*I_k + omega_k
% U_k = K_0 - K_1/S_k - K_2 * S_k + K_3*ln(S_k) + K_4*ln(1-S_k) - R*I_k - h_k*H + v_k
% h_k = {1, I_k > epsilon; -1, I_k < -epsilon; h_k-1, abs(I_k) <= epsilon}

% figure;
% hold on;
% plot(chg1.TotalTime', chg1.Voltage');
% plot(chg1.TotalTime', chg1.SOC_DOD/100');
% plot(chg1.TotalTime', chg1.Current');

% plot(dchg1.TotalTime', dchg1.Voltage');
% plot(dchg1.TotalTime', dchg1.SOC_DOD/100');
% plot(dchg1.TotalTime', dchg1.Current');

% hold off;


epsilon = 0.001;
energy_typical = 10.1; % Wh


soc = [(energy_typical-dchg1.Energy)' chg2.Energy' (energy_typical-dchg2.Energy)' (energy_typical+pulse1.Energy)']/energy_typical;
current = [-dchg1.Current' -chg2.Current' -dchg2.Current' pulse1.Current'];
voltage = [dchg1.Voltage' chg2.Voltage' dchg2.Voltage' pulse1.Voltage'];

M = zeros(length(voltage), 1);

for idx=1:length(soc)
    if soc(idx) == 0
        soc(idx) = 0.0001;
    end
    if soc(idx) == 1
        soc(idx) = 0.9999;
    end
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


vars = M\voltage';

figure;
plot(chg2.Energy/energy_typical, chg2.Voltage, "Color", "red", "LineWidth", 2);
xlabel('State of Charge (SOC)');
ylabel('Voltage (V)');
title('Voltage vs. State of Charge');
grid on;

hold on;

soc_test = 0.001:0.001:0.999;

ocv = vars(1) - vars(2)./soc_test - soc_test*vars(3) + vars(4)*log(soc_test) + vars(5) * log(1 - soc_test);

chg = ocv - vars(6) * 0.56 + vars(8);
dchg = ocv - vars(7) * 0.56 - vars(8);

plot(soc_test, ocv, "Color", "red", "LineWidth", 0.5);
plot(soc_test, chg, "Color", "green", "LineWidth", 0.5);
plot(soc_test, dchg, "Color", "blue", "LineWidth", 0.5);

