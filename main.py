import cvxpy as cvx
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

BATTERY_POWER = 10
BATTERY_ENERGY = 10
EFFICIENCY = .85
MAX_CYCLES = 400

start = pd.to_datetime('2018-01-01')
end = pd.to_datetime('2019-01-01')
time_range = pd.date_range(start=start, end=end, freq='30min')

pd.np.random.seed(0)
min_bid_price = cvx.Parameter(
    name='min_bid_pri', 
    value=np.random.randn(len(time_range))*10 + 35,
    shape=len(time_range),
)
max_offer_price = cvx.Parameter(
    name='max_off_pri',
    value=np.random.randn(len(time_range))*10 + 120,
    shape=len(time_range),
)

bid_price = min_bid_price+10
offer_price = max_offer_price-10

# bid_price = cvx.Variable(len(time_range), name='bid_pri')
# offer_price = cvx.Variable(len(time_range), name='off_pri')

bid_volume = cvx.Variable(len(time_range), name='bid_vol')
offer_volume = cvx.Variable(len(time_range), name='off_vol')

soc = cvx.Variable(len(time_range)+1, name='off_pri')

battery_cycles = cvx.sum(offer_volume)/BATTERY_ENERGY

constraints = [
    bid_volume >=0,
    offer_volume >= 0,
    soc >=0, 
    bid_volume <=BATTERY_POWER/2,
    offer_volume <=BATTERY_ENERGY/2,    
    soc[0] == soc[-1], 
    soc[1:] == soc[:-1] + bid_volume*EFFICIENCY**.5 - offer_volume/EFFICIENCY**.5,
    soc <= BATTERY_ENERGY,
    battery_cycles <= MAX_CYCLES/365*len(time_range)/48,
]

objective_fun = cvx.Maximize(
    cvx.sum(-bid_price*bid_volume +offer_price*offer_volume)
)

problem = cvx.Problem(objective_fun, constraints)
problem.solve(
    eps_abs=1e-4, 
    eps_rel=1e-3, 
    max_iter=5000, 
    verbose=1
)

bid_volume = bid_volume.value
offer_volume = offer_volume.value
soc = soc.value

bid_volume[bid_volume<0] = 0
offer_volume[offer_volume<0] = 0
soc[soc<0] = 0

bid_volume[bid_volume>BATTERY_POWER/2] = BATTERY_POWER/2
offer_volume[offer_volume>BATTERY_POWER/2] = BATTERY_POWER/2
soc[soc>BATTERY_ENERGY] = BATTERY_ENERGY

print('Cycles:', offer_volume.sum()/BATTERY_POWER/len(time_range)*365*48)
print(
    'Profit:', 
    (offer_volume*offer_price.value - bid_volume*bid_price.value).sum()
)

fig, ax = plt.subplots(2, 1)
ax[0].plot(time_range, soc[1:], label='state of charge')
ax[0].set_ylabel('MWh')
ax[1].plot(time_range, max_offer_price.value, label='max_offer_price')
ax[1].plot(time_range, min_bid_price.value, label='min_bid_price')
ax[1].set_ylabel('£/MWh')
[a.legend(loc=1) for a in ax]
plt.show()