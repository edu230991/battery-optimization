import cvxpy as cvx
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters

from ninja_api import load_pv_data, load_wind_data
register_matplotlib_converters()

BATTERY_POWER_START = 20
BATTERY_ENERGY_START = 20
WIND_CAPACITY = 200
EFFICIENCY = .85
MAX_CYCLES = 400
SPOT_VOLATILITY = 20

wind_data = load_wind_data().fillna(method='ffill').iloc[:24*7]
wind_data = wind_data*WIND_CAPACITY
time_range = wind_data.index

pd.np.random.seed(0)
spot_price = cvx.Parameter(
    name='spot', 
    value=np.random.randn(len(time_range))*SPOT_VOLATILITY + 55,
    shape=len(time_range),
)
wind_prod = cvx.Parameter(
    name='wind_prod', 
    value=wind_data.values.squeeze(),
    shape=len(time_range),
)
mean_spot_price = spot_price.value.mean()

charge = cvx.Variable(len(time_range), name='bid_vol')
discharge = cvx.Variable(len(time_range), name='off_vol')
soc = cvx.Variable(len(time_range)+1, name='off_pri')

results = pd.DataFrame()
for i in pd.np.linspace(.5, 5, 10):
    BATTERY_POWER = BATTERY_POWER_START*i
    for j in pd.np.linspace(.5, 5, 10):
        BATTERY_ENERGY = BATTERY_POWER*j
    
        battery_cycles = cvx.sum(discharge+charge)/2/BATTERY_ENERGY/len(time_range)*365*24

        constraints = [
            charge >=0,
            discharge >= 0,
            soc >=0, 
            charge <=BATTERY_POWER,
            discharge <=BATTERY_POWER,    
            soc[0] == soc[-1], 
            soc[1:] == soc[:-1] + charge*EFFICIENCY**.5 - discharge/EFFICIENCY**.5,
            soc <= BATTERY_ENERGY,
            battery_cycles <= MAX_CYCLES,
        ]

        revenue = cvx.multiply(spot_price, (wind_prod + discharge - charge))
        revenue_var = revenue - cvx.sum(revenue)/len(time_range)

        objective_fun = cvx.Minimize(
            cvx.sum(cvx.square(revenue_var))
        )

        problem = cvx.Problem(objective_fun, constraints)
        problem.solve(
            solver=cvx.OSQP,
            eps_abs=1e-3, 
            eps_rel=1e-6, 
            max_iter=50000, 
            verbose=0
        )

        old_revenue = spot_price.value * wind_prod.value
        new_revenue = revenue.value

        imp = (old_revenue.std()-new_revenue.std())/old_revenue.std()
        print('Battery cycles:', battery_cycles.value.round(2))
        print(
            'Volatility improvement:', 
            round((old_revenue.std()-new_revenue.std())/old_revenue.std()*100, 2), '%')

        results = results.append(pd.DataFrame({
            'energy': [BATTERY_ENERGY],
            'power': [BATTERY_POWER],
            'c_factor': [j],
            'imp': [imp]
        }))

results['c_factor'] = results['energy']/results['power']
results['power_share'] = results['power']/WIND_CAPACITY
pivoted = results.pivot(
    index='power_share', columns='c_factor', values='imp'
)

pivoted.plot()
plt.show()

import ipdb; ipdb.set_trace()


# fig, ax = plt.subplots(4,1,sharex=True)
# ax[0].plot(time_range, wind_prod.value, label='wind prod')
# ax[0].plot(time_range, wind_prod.value+discharge.value-charge.value, 
#            label='net prod')
# ax[1].plot(time_range, discharge.value, label='discharge')
# ax[1].plot(time_range, charge.value, label='charge')
# ax[2].plot(time_range, soc[1:].value, label='soc')
# ax[3].plot(time_range, new_revenue, label='new')
# ax[3].plot(time_range, old_revenue, label='old')

# [a.legend() for a in ax]
# plt.show()