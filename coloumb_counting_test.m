clear; clc; close all;

lookuptable = readtable("lookuptable.csv");

raw_data = readtable("../previous_data/Heimir/Test/Cycle Testing Save 5/Cycle Testing of P28B Cell1 Save5.csv");
test_data = raw_data(2:end, :);



discharge_idx = test_data.Current < 0;
test_data.SOC_DOD(discharge_idx) = 100-test_data.SOC_DOD(discharge_idx);


charge_idx = test_data.Current > 0;
max_dischage_cap = max(test_data.Capacity(discharge_idx));
max_charge_cap = max(test_data.Capacity(charge_idx));

nom_capacity = 2650;

mu_cc = max_charge_cap*1000/nom_capacity;
mu_dc = max_dischage_cap*1000/nom_capacity;

first = true;
initial_soc = 0;

soc_history = zeros(length(test_data.TotalTime), 2);
for k=1:length(test_data.TotalTime)
    if first
        init_volt = test_data.Voltage(k);
        for i=1:length(lookuptable.Var1)
            if lookuptable.Var2(i) > init_volt
                % Find first SOC with a higher voltage than this one
                diff1 = lookuptable.Var2(i) - lookuptable.Var2(i-1);
                diff2 = lookuptable.Var2(i) - init_volt;
                initial_soc = lookuptable.Var1(i-1) + (diff2/diff1);
                soc_history(1,1) = initial_soc;
                soc_history(1,2) = initial_soc/100 * nom_capacity;
                break
            end
        end
        first = false;
    else
        delta_time = test_data.TotalTime(k) - test_data.TotalTime(k-1);
        delta_time = seconds(delta_time) / 3600; % Hours
        current = test_data.Current(k) * 1000; % mA
        if test_data.Current(k) > 0
            mu = mu_cc;
        else
            mu = mu_dc;
        end
        spent_capacity = current * delta_time * mu;
        soc_history(k, 2) = soc_history(k-1,2) + spent_capacity;
        soc_history(k, 1) = 100 * soc_history(k, 2) / nom_capacity;
    end
    
end
%%
time = test_data.TotalTime;
known_goods = test_data.StepIndex == 2 | test_data.StepIndex == 4 | test_data.StepIndex == 7 | test_data.StepIndex == 9 ...
    | test_data.StepIndex == 11 | test_data.StepIndex == 13 | test_data.StepIndex == 15 | test_data.StepIndex == 17;
exclude_idx = test_data.CycleIndex ~= 1 & known_goods & abs(test_data.SOC_DOD - soc_history(:, 1)) < 25;

mean_soc_error = mean(abs(soc_history(exclude_idx) - test_data.SOC_DOD(exclude_idx)))
max_soc_error = max(abs(soc_history(exclude_idx) - test_data.SOC_DOD(exclude_idx)))

%% Plot SOC Testing Apparatus vs SOC MATLAB
close all;


%% 
hold on
plot(time, test_data.SOC_DOD);
fig=gcf;
fig.Units = "centimeters";
fig.Position(3:4)=[16,12];

plot(time, soc_history(:, 1));
ylabel("SOC [%]")
yyaxis right
plot(time, test_data.Current);
legend("SOC Testing Apparatus", "SOC MATLAB", "Current");