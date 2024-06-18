import pandas as pd, numpy as np
import os

# read EV availability data (created by Switch data/import_data.py/ev_adoption_advanced())
# For each slice of a 100% EV fleet for Oahu, for each timestep, this 
# shows the fraction of that hour when the vehicles could charge 
# (chargeable_hours_in_step), the total duration of charge needed
# across all timesteps (charge_duration) and the total MW used for
# charging at full power.
timesteps = pd.read_csv(os.path.join("Input", "EV_charging_requirements.csv"))
# drop all but "Passenger gasoline vehicle"
timesteps = timesteps.query('vehicle_type == "Passenger gasoline vehicles"')
# downscale to one vehicle per profile, undo energy_adjustment for fleet
# and convert to kW
timesteps['charging_kw'] = (
    timesteps['charging_mw'] * 1000 
    / timesteps['energy_adjustment'] 
    / timesteps['n_vehicles']
)
# just keep the columns we want
timesteps = timesteps[[
    'veh_id', 
    'hour', 'charge_timestep', 'chargeable_hours_in_step',
    'charge_duration', 'charging_kw'
]]

# create random-ordered list of all Oahu "Passenger gasoline vehicle" profiles
rand = np.random.Generator(np.random.PCG64(99999)) # use consistent sequence
ids = timesteps['veh_id'].unique()
rand.shuffle(ids)
veh_pool = pd.DataFrame({
    'veh_id': ids
})

# prices = pd.DataFrame({'hour': range(24), 'price': [10 * n for n in range(24)]})
# prices = pd.DataFrame({'hour': range(24), 'price': [0.409352388, 0.02, 0.02, 0.02, 0.020141007, 0.025100926, 0.046257227, 0.498996358, 0.202351751, 0.02, 0.170649518, 1.02, 0.079885114, 0.197999425, 0.095801533, 0.038647371, 0.259759301, 0.02, 0.100030299, 0.043216126, 0.02, 0.140415599, 0.02155624, 0.094112756]})
# vehicle_count = 2; max_price = 10
# get_ev_bid(prices, vehicle_count, max_price)

def get_ev_bid(prices, vehicle_count, max_price=None):
    """
    Accept a dataframe of prices ($/kWh) for one day (which should be evenly 
    spaced in integer-hour blocks), number of vehicles to model and maximum 
    price willing to pay for charging ($/kWh). Return a dataframe showing how
    much each vehicle will charge during each timestep. Vehicles are added to
    the pool in a fixed, random order, so repeated calls with different numbers
    of vehicles will have the same first n vehicles.
    """
    hours_per_step = int(24 / prices.shape[0])

    # pull the first n vehicles from the pool
    selected_vehicles = veh_pool.iloc[:vehicle_count, :]

    # get relevant rows from timesteps dataframe (will drop unmatched ones)
    selected_timesteps = selected_vehicles.merge(timesteps, on='veh_id', how='inner')

    # get prices for each possible charging timestep
    bid = selected_timesteps.merge(prices, on='hour')
    # sort by vehicle, price rank, hours since start of window; later, each 
    # vehicle will be charged in this order, respecting the price rank during
    # their charging window(s).
    bid = bid.sort_values(['veh_id', 'price', 'charge_timestep'])
    bid = bid.reset_index(drop=True).copy()

    # decide how much charging to do during each timestep
    # copied from Switch data/import_data.py
    charge_dur = []  # list of charge durations to apply to each row of bid frame
    prev_veh_id = None
    for r in bid.itertuples():
        if r.veh_id != prev_veh_id:
            # new vehicle, reset charge duration counter
            prev_veh_id = r.veh_id
            prev_dur = 0
        # charge as much as possible or as much as needed, whichever is less
        dur = min(r.chargeable_hours_in_step, r.charge_duration - prev_dur)
        prev_dur += dur
        charge_dur.append(dur)
    bid['charge_dur_in_timestep'] = pd.Series(charge_dur)
    bid['charge_kw'] = bid['charging_kw'] * bid['charge_dur_in_timestep'] / hours_per_step
    # record maximum possible charging in each timestep for use later
    bid['max_charge_kw'] = bid['charging_kw'] * bid['chargeable_hours_in_step'] / hours_per_step

    # don't charge in hours when price is more than max_price (may leave vehicle undercharged)
    if max_price is not None:
        bid.loc[bid['price'] >= max_price, 'charge_kw'] = 0

    # pivot data to have one column per vehicle, then fill in missing hours, 
    # sort the vehicles by their order in the pool, and give better labels
    final_bid = (
        bid.pivot(index="hour", columns="veh_id", values="charge_kw")
        .reindex(prices['hour'], axis=0)  # make sure all hours are present
        .fillna(0)
        .loc[:, selected_vehicles['veh_id']]
    )
    final_bid.columns = ['EV_{:03d}'.format(i) for i in final_bid.columns]
    final_bid = final_bid.reset_index() # recover hour column

    charge_windows = (
        bid.pivot(index="hour", columns="veh_id", values="max_charge_kw")
        .reindex(prices['hour'], axis=0)  # make sure all hours are present
        .fillna(0)
        .loc[:, selected_vehicles['veh_id']]
    )
    charge_windows.columns = ['EV_{:03d}_max'.format(i) for i in charge_windows.columns]
    charge_windows = charge_windows.reset_index() # recover hour column

    return final_bid, charge_windows
