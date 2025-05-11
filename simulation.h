#ifndef SIMULATION_H
#define SIMULATION_H
#include <stdint.h>

typedef struct
{
    uint16_t soc_estimation; // State of charge estimation
    uint16_t cell_capacity_estimation[3]; // Estimated remaining cell capacity in mAh
    uint16_t cell_voltages[3];
    uint16_t cell_temperatures[3];
    uint16_t current;
} Simulation_HandleTypeDef;

typedef struct
{
    uint16_t cell_voltages[3];
    uint16_t cell_temperatures[3];
    uint16_t current;
} Simulation_RX_TypeDef;

typedef struct
{
    uint16_t estimated_capacity[3]; // Estimated remaining cell capacity in mAh
    uint16_t estimated_soc[3]; // State of charge estimation
    uint16_t pack_soc; // Pack state of charge
} Simulation_TX_TypeDef;

#endif // SIMULATION_H