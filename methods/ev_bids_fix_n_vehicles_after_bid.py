import pandas as pd, numpy as np
import os, heapq

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

# prices = pd.DataFrame({'hour': range(24), 'price': [10 * n for n in range(24)]})
# vehicle_count = {'Passenger gasoline vehicles': 500, 'Freight gasoline vehicles': 10}

# copied from Switch data/import_data.py
def get_ev_bid(prices, vehicle_count=None, max_price=None):
    """
    Accept a dataframe of per-timestep EV charging data `timesteps` and a dataframe of prices
    or price ranks `prices` for one day (which should be evenly spaced in integer-hour blocks),
    and return a vector of electricity demand for each time step of the day.
    """
    hours_per_step = int(24 / prices.shape[0])

    # sort by vehicle, price rank, hours since start of window, then assign charging in order
    bid = timesteps.merge(prices, on='hour').sort_values(['veh_id', 'price', 'charge_timestep'])
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

    if vehicle_count is not None:
        # Adjust fleet size and charging power if vehicle count has been provided.
        # This assigns an integer weight to each sample vehicle, seeking to 
        # preserve the original distribution as closely as possible. This should
        # be stable between calls and fairly fast.

        # Get one row per vehicle (n_vehicles should be the same across all rows
        # for that vehicle, so we just use .mean() to get it)
        veh = bid.groupby(['vehicle_type', 'veh_id'])['n_vehicles'].mean().reset_index()
        # veh['n_vehicles'] = veh['n_vehicles_orig']
        veh['n_vehicles_orig'] = veh['n_vehicles']
        # work through all the vehicle types
        for t, grp in veh.groupby('vehicle_type'):
            # grp does not link back to the original dataframe, but we make a 
            # copy just to be sure.
            grp = grp.copy()
            # how much do we need to scale the original counts down (or up)?
            scale = vehicle_count.get(t, 0) / grp['n_vehicles_orig'].sum()
            # do initial rough assignment (helpful if we have 1 or more of each vehicle type)
            grp['n_vehicles'] = (scale * grp['n_vehicles_orig']).apply(np.floor)
            # how many more vehicles need to be added to reach the target?
            num_to_do = int(vehicle_count.get(t, 0) - grp['n_vehicles'].sum())
            # make a heap of all the errors (err, index)
            errs = [
                (r['n_vehicles'] - scale * r['n_vehicles_orig'], idx)
                for idx, r in grp.iterrows()
            ]
            heapq.heapify(errs)
            for i in range(num_to_do):
                # find the vehicle with the biggest error (most negative),
                # then increase its weighting by 1 and shrink the error by 1,
                # then put it back on the heap for possible further adjustment
                # later.
                err, idx = heapq.heappop(errs)
                grp.loc[idx, 'n_vehicles'] += 1
                heapq.heappush(errs, (err + 1, idx))
            # assign n_vehicles back to bid frame and rescale charge_mw
            upd = bid[['vehicle_type', 'veh_id', 'charge_mw']].merge(grp)
            upd['charge_mw'] *= upd['n_vehicles'] / upd['n_vehicles_orig']
            bid.update(upd[['n_vehicles', 'charge_mw']])

    bid_index = pd.MultiIndex.from_product([timesteps['vehicle_type'].unique(), prices['hour']])
    final_bid = bid.groupby(['vehicle_type', 'hour'])['charge_mw'].sum().reindex(bid_index).fillna(0)

    final_bid.index.names = ['vehicle_type', 'hour']
    final_bid = final_bid.reset_index()

    return final_bid
