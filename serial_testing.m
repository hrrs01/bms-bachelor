clear; clc; close all;
s = serialport("/dev/ttyACM0", 115200);

str = "Hello, World!";
write(s, str, "uint8");

result=read(s, strlength("Message Recieved:  " + str), "uint8");
string(char(result))

delete(s);