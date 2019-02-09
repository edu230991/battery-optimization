# battery-optimization

This is a simple example of how an optimization problem can be written to optimize profit for a battery storage unit playing in a pay-as-bid market.

The (big) assumption is that market prices, specifically the maximum offer price and the minimum bid price can be perfectly predicted at any time t. 
A fixed discount (or increase) from those is assumed to find the player's bid and offer price. 

The battery is constrained to start and end with the same state of charge, and yearly battery cycles are constrained to be smaller than a fixed quantity. 

The folling iterations can be done starting from here:
* the discount or increase from the market price become decision variables. The problem needs therefore to be linearized
* a call probability is assigned that decreases with increasing absolute values of price increase or discount. E.g. there is a lower chance of being called and therefore realizing a revenue if bid price is low or offer price is high.
* the volume that can be accepted by the TSO varies with the price level, according to a price curve
* optimization is done multi-stage to account for time lag in auctions
* cost of cycling the battery is included in the optimization, for example as a function of state of charge
* etc.