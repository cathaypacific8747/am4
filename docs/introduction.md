# AM4 101

Quick reference manual. See the list of [mathematical formulae](./formulae.md) for more precise information.

## Aircraft

An aircraft is associated with many attributes. Among the most important are:

- Maximum Range $R$: affects the frequency of departures and your access to more destinations.
- Engine Variant*: applies a multiplier on the *base* speed, fuel and CO<sub>2</sub> consumption values.
- Cruise Speed $V$*: ground speed of the aircraft, constant from the takeoff to final approach phase. can be increased with [modifications]()
- Fuel Consumption $c_T$*: can be decreased with [modifications]() and [training points]()
- CO2 Consumption $c_C$*: can be decreased with [modifications]() and [training points]()
- Capacity $C$: the maximum *units* of passengers or cargo, for use in [aircraft configuration](#aircraft-configuration).
- Minimum Runway Length $L_\text{rwy,min}$: [restricts](#constraints) the route choices for realism players

\* A common question is the discrepancy between aircraft specifications in the menu page and the detailed order page. The menu page lists the *base* specifications - clicking into the detailed order page applies a multiplier (typically 0.95-1.05) to the base specifications.

The list of aircrafts can be downloaded [here]().

## Airport

The list of airports can be downloaded [here]().

## Routing

Consider a *route* from origin airport $A$ to a destination $C$, with the [haversine distance](./formulae.md#distance) $d_\text{AC}$.

### Demand

Each route is uniquely associated with a daily demand for economy class $D_y$, business class $D_j$, first class $D_f$, large cargo $D_l$ and heavy cargo $D_h$.

- When a flight departs, the demand decreases based on the number of seats sold or cargo carried.
- Once the demand of a class reaches zero, no futher profit is earned from that class.
- Demand is refilled daily at 01:00 UTC.
- Demand is undirected (routes $A \rightarrow C$ and $C \rightarrow A$ share the same demand).
- The average demand to a destination is correlated with the [base hub cost]() of the origin.

### Constraints

- A route may contain one leg ($A \rightarrow C$), or two legs ($A \rightarrow B \rightarrow C$, via stopover $B$).
- The direct distance of each leg $d$ must be less than the aircraft range $R$.
- This means that the effective range of an aircraft can be doubled if a stopover is used.
- For realism players, the runway length $L_\text{rwy}$ of both origin and destinations and one leg must be greater than the aircraft minimum runway length $L_\text{rwy,min}$.

## Revenue

An aircraft has $C$ units of capacity and can be customised.

### Aircraft Configuration

Certain seat classes take up more "empty space" of the aircraft:

| Seat class | Units of capacity |
|-|-|
| Economy $y$ | 1 |
| Business $j$ | 2 |
| First $f$ | 3 |
| Large cargo $l$ | 0.7 |
| Heavy cargo $h$ | 1 |

The weighted sum of seats should add up to the capacity. For example, an A380-800 has $C=600$ units of capacity, and a valid configuration can be $s_y=100$, $s_j=100$ and $s_f=100$ because their weighted sum is $1 \cdot 100+2\cdot 100 + 3\cdot 100=600$.

### Ticket price

The ticket price for each class $p_i$ increases linearly with the *direct* distance $d_{AC}$ of a route.

More specifically, $p_i=m_i d_{AC} + c_i$, where $m_i$ and $c_i$ are [constants](./formulae.md#ticket-prices) depending on the specific seat class and game mode. Note that adding a stopover does not increase the ticket price, so an [optimal stopover]() should be selected to avoid extra detour.

In practice, a higher revenue per flight can be achieved by multiplying the autoprice-suggested ticket price with an appropriate constant. See the [formulae](./formulae.md#ticket-prices) for the upper bound. Exercise caution: flights may occasionally be empty due to rounding on AM4's servers - always subtract a few dollars to be safe. 

## Operating Expenses

### Marketing
### Fuel

The cost is a *psuedo*random value sampled from a uniform distribution, $300-$3000, updated every 30 minutes.

Fuel bonanzas with <$100 may occur, though it is extremely rare.

### CO2

The cost is a *psuedo*random value sampled from a uniform distribution, $100-$200, updated every 30 minutes.

CO2 bonanzas with $10 may occur, though it is extremely rare.

### Cost index

Decreasing the cost index (CI) reduces the speed of the aircraft, thus theoretically reducing the daily profit. Simultaneously, the fuel and co2 consumption is reduced, reducing the daily expenses.

Useful when trying to artifically inflate the flight time to match your departure schedule, or [increasing contribution](./formulae.md#contribution).

### Crew
### A-check
### Repair
### ferry flight

## Capital Expenditure

Purchasing a significant asset incurs a non-recurring cash outlay:

### Aircraft base cost
### Aircraft configuration cost
### Aircraft modification cost
### Hub cost

## Important Concepts

### Total number of aircraft ever purchased

Purchasing a new aircraft increments an internal counter, which increases the [marketing cost](#marketing) and [hub cost](#hub-cost).

Selling an aircraft does not decrement the counter.

The value can be inferred from the default registration on the aircraft order page.

## Alliances

An airline can form a new alliance or join an existing one.

Departing flights earn you a *contribution value*.
