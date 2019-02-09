# battery-optimization

This is a simple example of how an optimization problem can be written to optimize profit for a battery storage unit playing in a pay-as-bid market.

The (big) assumption is that market prices, specifically the maximum offer price and the minimum bid price can be perfectly predicted at any time t. 
A fixed discount (or increase) from those is assumed to find the player's bid and offer price. 

The battery is constrained to start and end with the same state of charge, and yearly battery cycles are constrained to be smaller than a fixed quantity. 