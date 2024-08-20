# Energy Trading Web Application

This web application is designed to optimize the operation of Electric Water Heaters (EWH) by balancing cost savings and user comfort. The application is based on advanced energy optimization methods, including mixed-integer linear programming (MILP), and simulates the performance of different methods to compare their effectiveness in reducing energy costs and maintaining comfort.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Overview

The primary objective of this application is to demonstrate the practical implementation of EWH optimization methods by allowing users to configure various parameters, simulate different optimization strategies, and analyze the results. The application provides insights into the trade-offs between energy cost reduction and user comfort.

The simulation results can be used to compare different methods, including:
- **MILP**: A method that minimizes both cost and user discomfort.
- **Du&Lu**: A method that considers both price and consumption patterns.
- **Apt&Goh**: A simple method focusing on price.
- **Fixed_Thermostat**: A baseline method representing a standard fixed setpoint thermostat.
- **Solar_EWH**: A method that incorporates solar energy to reduce grid dependency.

## Features

- **Dynamic Input Form**: Allows users to select from multiple optimization methods and configure various parameters.
- **Result Visualization**: Generates graphical representations of energy consumption patterns across different methods.
- **Cost & Discomfort Analysis**: Provides detailed comparisons of energy costs and user discomfort for each method.
- **Automatic Comparison**: Automatically compares each method's performance against the Fixed Thermostat method to calculate energy savings and discomfort reduction.

## Project Structure

The project is structured as follows:


### Key Files:

- **`form.html`**: The main form where users input parameters and select methods. The Fixed_Thermostat method is pre-selected and cannot be deselected.
- **`results.html`**: Displays the simulation results, including cost and discomfort analysis.
- **`Solve.py`**: Handles the optimization process based on user inputs.
- **`flask_application.py`**: The main web application logic that connects the form, the optimization process, and the results page.
- **`OneDayDF.csv`**: Contains the output data from the optimization, used to generate graphs and perform cost/discomfort analysis.

## Installation

To install and run this project locally:

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python flask_application.py
http://localhost:8000
