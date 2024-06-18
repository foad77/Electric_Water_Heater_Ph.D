import pandas as pd, numpy as np
import os

# read EV availability data (created by Switch data/import_data.py/ev_adoption_advanced())
# For each slice of a 100% EV fleet for Oahu, for each timestep, this 
# shows the fraction of that hour when the vehicles could charge 
# (chargeable_hours_in_step), the total duration of charge needed
# across all timesteps (charge_duration) and the total MW used for
# charging at full power.
timesteps = pd.read_csv(os.path.join("Input", "EV_charging_requirements.csv"))
# just keep the columns we want
timesteps = timesteps[[
    'veh_id', 'vehicle_type', 
    'hour', 'charge_timestep', 'chargeable_hours_in_step',
    'n_vehicles', 'charge_duration', 'charging_mw'
]]

# create random-ordered lists of all individual vehicles on Oahu 
# (each veh_id is repeated n_vehicles times in the whole set)
rand = np.random.Generator(np.random.PCG64(99999)) # use consistent sequence
veh = timesteps[['vehicle_type', 'veh_id', 'n_vehicles']].drop_duplicates().sort_values(['vehicle_type', 'veh_id'])
all_vehicles = {}
for vehicle_type, grp in veh.groupby('vehicle_type'):
    # if vehicle_type == "Passenger gasoline vehicles":
    #     break
    # create a random-ordered list of all the vehicles on Oahu
    all_ids = np.array([   # list of all vehicles on Oahu, one row per vehicle
        r['veh_id'] for idx, r in grp.iterrows() # : break
        for _ in range(int(round(r['n_vehicles'])))
    ])
    rand.shuffle(all_ids)
    all_vehicles[vehicle_type] = all_ids


# prices = pd.DataFrame({'hour': range(24), 'price': [10 * n for n in range(24)]})
# vehicle_count = {'Passenger gasoline vehicles': 500, 'Freight gasoline vehicles': 10}
# get_ev_bid(prices, vehicle_count, 1000)

# copied from Switch data/import_data.py
def get_ev_bid(prices, vehicle_count=None, max_price=None):
    """
    Accept a dataframe of per-timestep EV charging data `timesteps` and a dataframe of prices
    or price ranks `prices` for one day (which should be evenly spaced in integer-hour blocks),
    and return a vector of electricity demand for each time step of the day.
    """
    hours_per_step = int(24 / prices.shape[0])

    if vehicle_count is None:
        # use the whole fleet
        selected_timesteps = timesteps.copy()
        # vehicle_count = {t: len(ids) for t, ids in all_vehicles.items()}
    else:
        # pull the first n vehicles from the all_vehicles list and cluster duplicates
        selected_vehicles = pd.concat(
            pd.DataFrame({
                'vehicle_type': t,
                'veh_id': all_vehicles[t][:n]
            })
            for t, n in vehicle_count.items()
        ).groupby(['vehicle_type', 'veh_id']).size().to_frame('n_vehicles_target')

        # get relevant rows from timesteps dataframe (will drop unmatched ones)
        selected_timesteps = timesteps.merge(
            selected_vehicles, 
            on=['vehicle_type', 'veh_id'],
            how='inner'
        )
        selected_timesteps['charging_mw'] = selected_timesteps.eval(
            "charging_mw * n_vehicles_target / n_vehicles"
        )
        selected_timesteps['n_vehicles'] = selected_timesteps['n_vehicles_target']

    # get prices for each possible charging timestep
    bid = selected_timesteps.merge(prices, on='hour')
    # don't charge in hours when price is more than max_price (may leave vehicle undercharged)
    if max_price is not None:
        bid = bid[bid['price'] <= max_price]
    # sort by vehicle, price rank, hours since start of window; later, each 
    # vehicle will be charged in this order, respecting the price rank during
    # their charging window(s).
    bid = bid.sort_values(['vehicle_type', 'veh_id', 'price', 'charge_timestep'])
    bid = bid.reset_index(drop=True).copy()

    # decide how much charging to do during each timestep
    # The commented-out code runs surprisingly slowly (a couple seconds for a
    # few hundred vehicles) and also has index matching errors because the group
    # label gets added to the index. So we just use the simple for loop below instead.
    # def charge_dur(g):
    #     dur_charged = g['chargeable_hours_in_step'].cumsum().clip(upper=g['charge_duration'])
    #     prev_charged = dur_charged.shift(1).fillna(0)
    #     return dur_charged - prev_charged
    # bid['charge_dur_in_timestep'] = bid.groupby('veh_id').apply(charge_dur) #.values
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
    bid['charge_mw'] = bid['charging_mw'] * bid['charge_dur_in_timestep'] / hours_per_step

    bid_index = prices['hour']
    final_bid = bid.groupby('hour')['charge_mw'].sum().reindex(bid_index).fillna(0)
    
    final_bid.index.names = ['hour']
    final_bid = final_bid.reset_index()

    # calculate relative willingness to pay for this charging
    if max_price is None:
        # will charge as much as possible each iteration so wtp is constant
        # (could be 0 or any other number)
        wtp = 0
    else:
        # they were willing to pay up to max_price for every kWh they got
        wtp = final_bid['charge_mw'].sum() * max_price

    return wtp, final_bid
