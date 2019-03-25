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
RISK_METHOD = 'variance' # None

soc_scenarios = 9
price_scenarios = 500

initial_soc = np.linspace(BATTERY_ENERGY*.1, BATTERY_ENERGY*.9, soc_scenarios)
probability_soc = -(initial_soc-.5*BATTERY_ENERGY)**2 + (initial_soc[0] - .5*BATTERY_ENERGY)**2*1.1
probability_soc = probability_soc/probability_soc.sum()

start = pd.to_datetime('2018-01-01')
end = pd.to_datetime('2018-01-15')
time_range = pd.date_range(start=start, end=end, freq='30min')

pd.np.random.seed(0)
min_bid_price = cvx.Parameter(
    name='min_bid_pri', 
    value=np.random.randn(len(time_range), price_scenarios)*10 + 35,
    shape=(len(time_range), price_scenarios),
)
max_offer_price = cvx.Parameter(
    name='max_off_pri',
    value=np.random.randn(len(time_range), price_scenarios)*10 + 120,
    shape=(len(time_range), price_scenarios),
)

bid_price = min_bid_price + 10
offer_price = max_offer_price - 10

# bid_price = cvx.Variable(len(time_range), name='bid_pri')
# offer_price = cvx.Variable(len(time_range), name='off_pri')

bid_volume = cvx.Variable(len(time_range), name='bid_vol')
offer_volume = cvx.Variable(len(time_range), name='off_vol')
unreal_bid_volume = cvx.Variable((len(time_range), soc_scenarios), name='bid_vol')
unreal_offer_volume = cvx.Variable((len(time_range), soc_scenarios), name='off_vol')

soc = cvx.Variable((len(time_range)+1, soc_scenarios), name='off_pri')

battery_cycles = cvx.sum(offer_volume)/BATTERY_ENERGY

constraints = [
    bid_volume >=0,
    offer_volume >= 0,
    soc >=0, 
    bid_volume <=BATTERY_POWER/2,
    offer_volume <=BATTERY_ENERGY/2,    
    soc[0] == initial_soc, 
    soc <= BATTERY_ENERGY,
    battery_cycles <= MAX_CYCLES/365*len(time_range)/48,
    unreal_bid_volume >= 0,
    unreal_offer_volume >= 0,  
]
for i in range(soc.shape[1]):
    constraints += [unreal_bid_volume[:, i] <= bid_volume,
                    unreal_offer_volume[:, i] <= offer_volume]  
    constraints += [soc[1:, i] == 
        soc[:-1, i] + (bid_volume-unreal_bid_volume[:, i])*EFFICIENCY**.5 - 
        (offer_volume-unreal_offer_volume[:, i])/EFFICIENCY**.5,]

revenue = offer_price.T*offer_volume
cost = bid_price.T*bid_volume

lost_revenue = cvx.sum(cvx.multiply(unreal_offer_volume.T*cvx.sum(
    offer_price, axis=1)/offer_price.shape[0],
    probability_soc))
saved_cost = cvx.sum(cvx.multiply(unreal_bid_volume.T*cvx.sum(
    bid_price, axis=1)/bid_price.shape[0],
    probability_soc))

expected_profit = 1/price_scenarios*cvx.sum(revenue - cost) - lost_revenue
if RISK_METHOD == 'variance':
    risk = 1e-7*cvx.sum(cvx.power(revenue - cost, 2))
elif RISK_METHOD == None:
    risk = 0
objective_fun = cvx.Maximize(expected_profit - risk)

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
print('Expected profit:', expected_profit.value)
# print('Risk:', risk.value)

fig, ax = plt.subplots(2, 1, sharex=True)
ax[0].plot(time_range, soc[1:], label='state of charge')
ax[0].set_ylabel('MWh')
ax[1].plot(time_range, max_offer_price.value.mean(axis=1), label='max_offer_price')
ax[1].plot(time_range, np.percentile(max_offer_price.value, 75, axis=1), label='max_offer_price', color='gray')
ax[1].plot(time_range, np.percentile(max_offer_price.value, 25, axis=1), label='max_offer_price', color='gray')

ax[1].plot(time_range, min_bid_price.value.mean(axis=1), label='min_bid_price')
ax[1].plot(time_range, np.percentile(min_bid_price.value, 75, axis=1), label='max_offer_price', color='gray')
ax[1].plot(time_range, np.percentile(min_bid_price.value, 25, axis=1), label='max_offer_price', color='gray')

ax[1].set_ylabel('£/MWh')
# [a.legend(loc=1) for a in ax]
plt.show()
import ipdb; ipdb.set_trace()
