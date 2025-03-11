close all; clc; clear;

rawdata = readtable("Battery Bachelor Testdata/Heimir/Cycle Testing of P28B cell1/Cycle Testing of P28B cell1.csv");
% trim first line as it is always garbage for some reason
rawdata = rawdata(2:end, :);

% A zero state hysteris model is used, following the form
% S_(k+1) = S_k - ((n_k*delta(t))/C_n)*I_k + omega_k
% U_k = K_0 - K_1/S_k - K_2 * S_k + K_3*ln(S_k) + K_4*ln(1-S_k) - R*I_k - h_k*H + v_k
% h_k = {1, I_k > epsilon; -1, I_k < -epsilon; h_k-1, abs(I_k) <= epsilon}

epsilon = 0.001;

U = rawdata.Voltage;
I = -rawdata.Current; % Discharge is positve, and vise verca

