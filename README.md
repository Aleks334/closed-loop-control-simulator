# Compressor Pressure Control System Simulator

## Overview
This project is a simulation of an automatic pressure regulation system for a compressed air tank. The primary objective is to maintain a target pressure level within the tank despite disturbances caused by air leakage (mass outflow). The application provides an interactive interface to adjust system parameters and regulator settings while observing the system's response in real-time.

## Theoretical Background
The object of regulation is described by a simplified dynamic model based on the mass balance of gas in the tank and the Ideal Gas Law. The physical dynamics of pressure changes in continuous time are defined by the following differential equation:

$$\frac{dp(t)}{dt} = \frac{R \cdot T}{V} \cdot (m_{in}(t) - m_{out}(t))$$

Where:
* **V**: Tank volume
* **T**: Gas temperature
* **R**: Individual gas constant
* **m_in**: Mass inflow (controlled variable)
* **m_out**: Mass outflow (disturbance/leakage)

The simulation utilizes the Euler method to solve the differential equation in discrete time steps. A PI (Proportional-Integral) controller is implemented to minimize the error between the setpoint and the actual pressure.

## Features
* **Interactive Simulation:** Adjust the target pressure, tank volume, and leakage coefficient.
* **Controller Tuning:** Real-time modification of PI regulator parameters ($K_p$, $T_i$).
* **Visualization:** Live plotting of:
    * Pressure response ($p$) vs. Setpoint ($p^*$)
    * Control signal ($u$)
    * Mass flow rates ($m_{in}$, $m_{out}$)

## Getting Started

### Installation
1.  Clone this repository or download the source code.
2.  Install the required dependencies using pip:

    ```bash
    pip install dash plotly numpy
    ```

### Usage
1.  Run main app script:

    ```bash
    python main.py
    ```

2.  Open your web browser and navigate to `http://127.0.0.1:8050/`.
3.  Set the desired parameters using the sliders and click **"Uruchom symulację"** (Start Simulation) to generate the graphs.