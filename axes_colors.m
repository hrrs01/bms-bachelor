% Demo to make a black graph with red Y axis, green X axis, and yellow grid.  Markers are magenta with green lines between them.
% Initialization steps:
clc;    % Clear the command window.
close all;  % Close all figures (except those of imtool.)
clearvars;
workspace;  % Make sure the workspace panel is showing.
format long g;
format compact;
fontSize = 24;

% Create sample data.
X = 1 : 20;
Y = rand(1, 20);
% Plot green lines between the markers.
plot(X, Y, 'g-', 'LineWidth', 3);
hold on;
% Plot magenta markers.
plot(X, Y, 'ms', 'LineWidth', 3, 'MarkerSize', 15);
grid on;
title('Y vs. X, Font Size 20', 'FontSize', 20, 'Color', 'b', 'FontWeight', 'bold');
% Make labels for the two axes.
xlabel('X Axis, Font Size 18');
ylabel('Y axis, Font Size 24');
yticks(0 : 0.2 : 1);
% Get handle to current axes.
ax = gca

% Now let's have fun changing all kinds of things!
% This sets background color to black.
ax.Color = 'k'
ax.YColor = 'r';
% Make the x axis dark green.
darkGreen = [0, 0.6, 0];
ax.XColor = darkGreen;
% Make the grid color yellow.
ax.GridColor = 'y';
ax.GridAlpha = 0.9; % Set's transparency of the grid.
% Set x and y font sizes.
ax.XAxis.FontSize = 18;
ax.YAxis.FontSize = 24;
% Make the axes tick marks and bounding box be really thick.
ax.LineWidth = 3;
% Let's have the tick marks go outside the graph instead of poking inwards
ax.TickDir = 'out';
% The below would set everything: title, x axis, y axis, and tick mark label font sizes.
% ax.FontSize = 34;
% Bold all labels.
ax.FontWeight = 'bold';
hold off

% Now do stuff with the figure, as opposed to the axes control that is ON the figure.
% Maximize the figure
g = gcf; % Get handle to the current figure.
g.WindowState = 'maximized'; % Make it full screen.
g.Name = 'Demo by Image Analyst'; % Put a custom string into the titlebar.
g.NumberTitle = 'off'; % Don't have it put "Figure 1" before the name.
g.MenuBar = 'figure'; % or 'none'
g.ToolBar = 'figure'; % or 'none'
