# How do configure an aircraft?

> Imagine going to a camping trip. You have a limited space in your 
> backpack and you want to pack the items that are most useful to you.
> How would you determine the best way to pack the backpack?

The ultimate goal is make sure you can:

- understand the general process of seat configuration in a simplified example
- understand the interplay between ticket prices and seat classes
- explain when and why it's better to do YJF or FJY.
- formulate an algorithm that optimally finds the configuration given the route distance and demand

This guide is written for technical players who want to learn the principles of the game mechanics.

Reading time: ~15 minutes.

Skip to [TLDR](#tldr) for a quick summary.

## Easy

Let's simplify the problem:

!!! abstract "Example"

    Consider a hypothetical plane with *only* economy and business class.
    Both $y$ and $j$ class both occupy one "unit" of capacity.

    Visualising it:
    ```
    Demand: yyyyyyyyyyjjj  10y-class, 3j-class
    Config: ______         one aircraft has total capacity 6
            ______         we fly it twice a day
    ```

    $y$ class pays \$1 and $j$ class pays \$2: we want to carry the j-class people first.

    Find the optimal configuration.

**Plan 1**: fill the configuration with $j$ class *only*
```
Flight 1: jjjjjj
             ^^^ 
       2: jjjjjj
          ^^^^^^ ❌ bad: not enough j demand! 9 empty seats!
```
We earned $3 \times 2 = \$6$ only.

**Plan 2**: fill the configuration with $y$ class *only*
```
Flight 1: yyyyyy

       2: yyyyyy
              ^^ ❌ bad: not enough y demand! 2 empty seats!
```
We earned $6×\$1 + 4×\$1 = \$10$.

But we can do better by taking the best of both worlds.

**Plan 3**:

Fill the configuration with the most valuable class ($j$ class) first.

- we have 3 j-demands and we don't want it to run out after 2 flights.
- so each flight should have at most, $\frac{3}{2} = 1.5$ seats.
- we should therefore *try* fill in 1 seat per flight:

```
Flight 1: j_____

       2: j_____

```

Fill the remaining slots with $y$ class:

- we have 10 y-demands and we don't want it to run out after 2 flights.
- so each flight should have on average, $\frac{10}{2} = 5$ seats.
- we should therefore *try* fill in max 5 seats per flight:

```
Flight 1: jyyyyy

       2: jyyyyy

```

Great! We earned $2(1\times\$2 + 5\times\$1) = \$14$!

### Sheets Exercises

Consider the following Sheet:
```
   A         B
1  y demand  j demand
2  capacity  number of flights
3
```

??? question "1. Write functions to calculate the optimal configuration."

    - **Fill in j-class**: each flight should have $\frac{\text{j demand}}{\text{number of flights}}$ j seats
    
    ``` title="Cell B3"
    FLOOR(B1 / B2)
    ```

    - **Calculate y-class seats**: each flight should have $(\text{capacity}-\text{j seats})$ y seats
    
    ``` title="Cell A3"
    A2 - B3
    ```

??? question "2. A route is suboptimal when there is *insufficient demand*. Add an error if this happens. (tip: consider a demand of 4Y, 3J for the same aircraft)"

    Example:

    1. 3J ÷ 2 flights = 1.5J per flight (rounding down to 1J per flight)
    ```
    Flight 1: j_____
           2: j_____
    ```
    
    2. Filling in the rest with Y class
    ```
    Flight 1: jyyyyy
           2: jyyyyy
    ```
    Notice that we have 5Y seats but only 2Y demand left. There is insufficient demand.

    We want to show an error if the demand left $\left(\frac{\text{y demand}}{\text{number of flights}}\right)$ is less than our computed Y seats.

    We can use the `IF(condition, true_value, false_value)` formula:
    
    ``` title="Cell A4"
    IF(FLOOR(A1/B2) < A3, "INSUFFICIENT DEMAND", "OK")
    ```
    
### Key Takeaways

The number of seats per flight is $\frac{\text{demand}}{\text{number of flights}}$, rounded down.

If we want to configure aircraft with two classes:

1. fill in the highest paying class first
2. allocate the remaining seats to the lower paying class
3. if the amount of seats in the lower paying class exceeds its demand, the route is suboptimal.

As you may imagine, we can generalise this algorithm to three classes (pax aircraft).

## Intermediate

In AM4, the key point to remember is that **one seat can use up multiple "units" of the aircraft capacity**.

|Seat Class|Capacity|
|-|-|
|$y$|1 unit|
|$j$|2 units|
|$f$|3 units|

!!! abstract "Example"
    Consider a plane with 2 economy $y$, 2 business $j$, and 3 first class $f$ seats.

    ```
    y y jj jj fff fff fff
    1 2 1  2  1   2   3
    ```
    If you count up the letters, we have $2\times1 + 2\times2 + 3\times3 = 15$ "units" of capacity.
    
    But we call this configuration "2Y 2J 3F", or 7 seats in total.

??? question "A plane has 13 capacity, 2 $j$ and 5 $y$ seats. How many $f$ seats should it have?"
    
    We know that the sum of "units" should add up to the capacity, so:
    
    $$
    \begin{align*}
    y+2j+3f &= \text{capacity} \\
    f &= \frac{\text{capacity}-2j-y}{3} \\
    &= \frac{12-4-5}{3} = 1
    \end{align*}
    $$

    Note: if there were 6 $y$ seats instead, we would compute $f=\frac{2}{3}$ which will be rounded down to 0.

    It is perfectly OK if $y+2j+3f$ don't add up to the capacity.

Now, let's reconsider the example from the [easy](#easy) section:

!!! abstract "Example"

    Consider a hypothetical route without first class demand:

    ```
    Demand: yyyyyyyyjjjjjj  8y-class, 6j-class
    Config: ______          one aircraft has total capacity 6
            ______          we fly it twice a day
    ```

    $y$ class pays \$1 and $j$ class pays \$1.5.

    Should we fill in $y$ first or $j$ first?

Well, you may answer of course $j$ because it pays more.

Let's try it, remembering 1J = 2 "units" of capacity:

```
Demand: yyyyyyyy···jjj
Config: jjjjjj    
        jjjjjj    
```

3J earned us $2(3\times\$1.5) = \$9$.

Doing the other way round: filling with y first:

```
Demand: ········jjjjjj    Demand: ··········jjjj
Config: yyyy__         -> Config: yyyyjj        
        yyyy__                    yyyyjj        
```

4Y1J earned us $2(4\times\$1+1\times1.5) = \$11$!

The higher paying class does not always mean we should always fill them in first:
they also "waste" the available capacity.

To determine which class is "objectively" better, let us create a score
$\frac{\text{expected income}}{\text{units of capacity}}$. Intuitively, a higher
ticket price will give us a better score, and higher units of capacity will decrease
the score.

In our example:

$$
\begin{align*}
\text{score}_j &= \frac{\$1.5}{2} = \$0.75\text{ per unit of capacity} \\
\text{score}_y &= \frac{\$1}{1} = \$1\text{ per unit of capacity}
\end{align*}
$$

So, a plane *full* of $y$ seats would give us 33% more profit than a plane full of $j$ class.
Indeed, our example matches this observation.

### Concept Check

Now, it's time to actually calculate which class is better in AM4. The formula for [pax ticket prices](../formulae.md#ticket-prices) in easy mode are:

$$
\begin{align*}
\$_\text{Y} &= 0.4d+170 \\
\$_\text{J} &= 0.8d+560 \\
\$_\text{F} &= 1.2d+1200 \\
\end{align*}
$$

Here, the ticket prices $\$$ increase when distance $d$ increases. The optimal multipliers are 1.1, 1.08, 1.06 respectively.


??? question "1. In what order should we fill seats in at a distance of 4000km (using default autoprice)?"
    
    We should compute the "score", or the expected income per unit capacity for each class:
    
    $$
    \begin{align*}
    \text{score}_y &= \frac{0.4\times4000+170}{1} = \$1770 \text{ per unit} \\
    \text{score}_j &= \frac{0.8\times4000+560}{2} = \$1880 \text{ per unit} \\
    \text{score}_f &= \frac{1.2\times4000+1200}{3} = \$2000 \text{ per unit} \\
    \end{align*}
    $$
    
    The order should be $f>j>y$.

??? question "2. How much more profit would we earn if we had filled in a full plane of $f$ class instead of $y$ class, at a distance of 13000km (using the autoprice multipliers)?"
    
    Computing the "score" for $d = 13000$:

    $$
    \begin{align*}
    \text{score}_y &= \frac{1.1(0.4\times13000+170)}{1} = \$5907 \text{ per unit} \\
    \text{score}_j &= \frac{1.08(0.8\times13000+560)}{2} = \$5918 \text{ per unit} \\
    \text{score}_f &= \frac{1.06(1.2\times13000+1200)}{3} = \$5936 \text{ per unit} \\
    \end{align*}
    $$
    
    The order should be $f>j>y$. But notice each of them are almost equally as good: $f$ class only gives us $\frac{5936-5907}{5907} = 0.49\%$ more profit.

    Practically, doing $y>j>f$ might actually be better if there's a lot of $y$ demand.


??? question "3. When should we choose $y>j>f$? (using the autoprice multipliers)?"

    That means our "score" should follow the following relationships:
    
    - $\text{score}_y$ should be greater than $\text{score}_j$
    - $\text{score}_j$ should be greater than $\text{score}_f$

    For the first relation, we have:
    
    $$
    \begin{align*}
    \frac{1.1(0.4d+170)}{1} &\gt \frac{1.08(0.8d+560)}{2} \\
    1.1(0.4d+170) &\gt 0.54(0.8d+560) \\
    1.1(0.4d)-0.54(0.8d) &\gt 0.54(560)-1.1(170) \\
    0.008d &\gt 115.4 \\
    d &\gt 14425
    \end{align*}
    $$

    Similarly for the second relation, we have:
    
    $$
    \begin{align*}
    \frac{1.08(0.8d+560)}{2} &\gt \frac{1.06(1.2d+1200)}{3} \\
    3\cdot0.54(0.8d+560) &\gt 1.06(1.2d+1200) \\
    1.62(0.8d)-1.06(1.2d) &\gt 1.06(1200)-1.62(560) \\
    0.024d &\gt 364.8 \\
    d &\gt 15200
    \end{align*}
    $$

    To satisfy both relations, ${d>14425 \cup d>15200}$ means $d>15200 \text{km}$.

    Here is a graph to illustrate this (try clicking at the intersection):
    <iframe class="desmos" src="https://www.desmos.com/calculator/7jefcotmgd?embed" width="100%" height="300" frameborder=0></iframe>

We are interested in the question:
> How much extra income would we gain by filling $f$ seats over $y$ seats?

We can compute ratio between the $f$ score and the $y$ score:

$$
\begin{align*}
\frac{\text{score}_f}{\text{score}_y}&=\frac{\frac{1.06(1.2d+1200)}{3}}{\frac{1.1(0.4d+170)}{1}} \\
&=\frac{0.424d+424}{0.44d+187}
\end{align*}
$$
<iframe class="desmos" src="https://www.desmos.com/calculator/gr3gmp7w3q?embed" width="100%" height="300" frameborder=0></iframe>

At a distance of 2000 km, we can gain $19.2\%$ more profit. But as the distance $d$ increases, we have diminishing returns and approach the break-even point at $14812.5$ km.

### Key Takeaways

- $y$, $j$, $f$ class seats each occupy different units of capacity.
- we can calculate the "score" for each class with $\frac{\text{expected income}}{\text{units of capacity}}$
- we should fill seats with the highest score first.
    - however, the configuration order doesn't matter when you use the multipliers.
    - use $y>j>f$ for extra long range distances (>15200km), otherwise stick to $f>j>y$.

## Advanced

Now let's consolidate everything and construct the pax algorithm in Sheets!

Consider the following Sheet:
```
   A         B                  C
1  y demand  j demand           f demand
2  capacity  number of flights
3
```

Suppose we wanted to calculate the $f>j>y$ configuration in row 3.

Here is the initial plan:

1. We need to fill the highest paying $f$ seats first:
    - $\text{seats}_f = \frac{\text{demand}_f}{\text{number of flights}}$, rounded down
    - `CHECK1`
2. Fill the $j$ seats next:
    - $\text{seats}_j = \frac{\text{demand}_j}{\text{number of flights}}$, rounded down
    - `CHECK2`
3. Fill the remaining seats with $y$:
    - $\text{seats}_y = \text{capacity} - \text{seats}_j \times 2 - \text{seats}_f \times 3$
    - `CHECK3`

??? question "Explain what needs to be put in `CHECK`."
    
    We need to make sure the seats actually makes sense: it doesn't exceed the capacity remaining.

    Suppose a plane with capacity 100, demand `0Y 1000J 0F` and 2 flights per day.
    
    - the naive calculation $\text{seats}_j = \frac{1000}{2} = 500$ exceeds the capacity.
    - we need to cap it at $\text{capacity}/2 = 50$ instead.

    Fixes:

    - `CHECK1`: make sure the calculated $\text{seats}_f \times 3 < \text{capacity}$. If it fails, set $\text{seats}_f = \frac{\text{capacity}}{3}$
    - `CHECK2`: make sure the calculated $\text{seats}_j \times 2 + \text{seats}_f \times 3 < \text{capacity}$. If it fails, set $\text{seats}_j = \frac{\text{capacity} - \text{seats}_f \times 3}{2}$
    - `CHECK3`: make sure the calculated $\text{seats}_y < \text{demand}_y/\text{number of flights}$, that is, there is sufficient demand remaining for us to carry.

### Implementation

??? question "1. Write a function in Cell C3 that does Step 1."
    
    The initial solution:
    ``` title="Cell C3"
    FLOOR(C1/B2)
    ```

    `CHECK1`: if the initial solution exceeds the capacity:
    
    - fill it with the remaining capacity ($\frac{\text{capacity}}{3}$), rounded down
    - otherwise, keep the initial solution
    
    ``` title="Cell C3"
    IF((FLOOR(C1/B2)*3) < A2, FLOOR(C1/B2), FLOOR(A2/3))
    ```

    Another way to do it is to grab the minimum between it and the equivalent capacity:
    ``` title="Cell C3"
    MIN(FLOOR(C1/B2), FLOOR(A2/3))
    ```

??? question "2. Write a function in Cell B3 that does Step 2."

    The initial solution:
    ``` title="Cell B3"
    FLOOR(B1/B2)
    ```

    `CHECK2`: if the initial solution (combined with the previously calculated $\text{seats}_f$) exceeds the capacity:

    - fill it with the remaining capacity ($\frac{\text{capacity} - 3\times\text{seats}_f}{2}$), rounded down
    - otherwise, keep the initial solution
    
    ``` title="Cell B3"
    IF((FLOOR(B1/B2)*2 + C3*3) < A2, FLOOR(B1/B2), FLOOR((A2 - C3*3)/2))
    ```

    A simpler way to do it:
    ``` title="Cell B3"
    MIN(FLOOR(B1/B2), FLOOR((A2 - C3*3)/2))
    ```

??? question "3. Write a function in Cell A3 that does Step 3. Show an error in Cell A4 (if any)."

    The initial solution:
    ``` title="Cell A3"
    A2 - C3*3 - B2*2
    ```

    `CHECK3`: if this solution is greater than the remaining $\text{demand}_y$:
    there are no demand remaining and we should show an error in `Cell A4`.
    
    ``` title="Cell A4"
    IF(A3 > FLOOR(A1/B2), "INSUFFICIENT DEMAND", "VALID")
    ```

??? question "4. If you are familiar with Python, write an implemention for the $f>j>y$ configuration. It should take inputs `yd: int`, `jd: int`, `fd: int` (demand per flight) and `capacity: int` , returning `tuple[int, int, int, bool]` (indicating the validity)."

    A possible solution:
    ```py
    def calc_fjy_conf(yd, jd, fd, capacity):
        fs = min(fd, capacity // 3)
        capacity -= fs * 3  # (1)!
        js = min(jd, capacity // 2)
        capacity -= js * 2  # (2)!
        ys = capacity # (3)!
        valid = ys < yd
        
        return (ys, js, fs, valid)
    ```
    
    1. Step 1: Fill first class seats first, and subtract from the available capacity.
    2. Step 2: Fill business class seats, and substract from the available capacity.
    3. Step 3: The capacity remaining should just be the y seats.

### Cargo

Cargo is has a similar mechanic to pax aircraft:

|Cargo Class|Capacity|
|-|-|
|Large, $l$|$\frac{10}{7}$ units|
|Heavy, $h$|1 unit|

For example, a cargo aircraft with 100000 lbs capacity with 100% large cargo can only take $100000\times0.7 = 70000$ lbs. The formula for [cargo ticket prices](../formulae.md#cargo) in easy mode are:

$$
\begin{align*}
\$_\text{L} &= 0.0948283724581252d + 85.2045432642377000 \\
\$_\text{H} &= 0.0689663577640275d + 28.2981124272893000 \\
\end{align*}
$$

The ticket price $\$$ also increase when distance $d$ increases. The autoprice multipliers are 1.1 and 1.08 respectively.

??? question "At what distances should we choose $l > h$?"

    Using the score function we developed early, we require:
    
    $$
    \begin{align*}
    \frac{\text{expected income}}{\text{units of capacity}}_l &\gt \frac{\text{expected income}}{\text{units of capacity}}_h \\
    \frac{1.1(0.094828d + 85.20454)}{\frac{10}{7}} &\gt \frac{(1.08(0.068966d + 28.29811))}{1} \\
    -0.0014658d &\gt -35.04554 \\
    d &\lt 23908.49
    \end{align*}
    $$

    Since the earth's half-circumference is $6371\pi=20015$km, we should choose $l > h$ for almost all flights.
    
    <iframe class="desmos" src="https://www.desmos.com/calculator/8gxc0f5sob?embed" width="100%" height="300" frameborder=0></iframe>

??? question "Develop a plan for the $l>h$ configuration formula."

    1. Fill the highest paying cargo: $l$:

        - $\text{\%}_l=\min\left(\frac{\text{demand}_l / \text{number of flights} \times 10/7}{\text{capacity}}, 100\%\right)$

    2. Fill the remaining with $h$ cargo:

        - $\text{\%}_h=1-\text{\%}_l$
        - Check $\frac{\text{demand}_h}{\text{number of flights}} \ge \text{capacity} \times \text{\%}_h$

??? question "If you are familiar with Python, write an implementation for the $l > h$ configuration. It should take in `ld: int`, `hd: int` (demand per flight) and `capacity: int`, returning `tuple[float, float, bool]` (indicating the validity)."

    A possible solution:
    ```py
    def calc_l_conf(ld, hd, capacity, l_training = 0, h_training = 0):
        l_cap = capacity * 0.7 * (1 + l_training / 100.0)
        if ld > l_cap:  # (1)!
            return (1, 0, True)

        l = ld / l_cap  # (2)!
        h = 1 - l  # (3)!
        valid = hd >= capacity * h * (1 + h_training / 100.0)
        return (l, h, valid)
    ```

    1. Early exit in case the demand per flight exceeds our large capacity
    2. Step 1: Fill in large $l$ first.
    3. Step 2: Fill the remaining with $h$.

The aforementioned approach is a *greedy bang-for-buck heuristic* solution for the rod cutting problem. The optimal solution has exponentially many partitions - you may be interested in the [Bounded knapsack problem](https://en.wikipedia.org/wiki/Knapsack_problem) and [Genetic algorithms](https://en.wikipedia.org/wiki/Genetic_algorithm).

## TLDR


For a given (seat class, units of capacity, demand) pair and initial capacity:

- $\text{seats} = \frac{\text{demand}}{\text{flights per day}}$, rounded down
- remove $\text{seats} \times \text{units of capacity}$ from the capacity
- if there are no more capacity left, fill this seat using the previous iteration's leftover capacity.

!!! abstract "Example: TGPY-UTDD. A380 (capacity 600), YJF configuration."
    Demand: 1779Y, 395J, 198F, 6 flights per day.

    |Seat Class|Seats|Seats to fill|
    |-|-|-|
    |Y|$\left\lfloor\frac{1779}{6}\right\rfloor = 296$|$600-296 = 304$|
    |J|$\left\lfloor\frac{395}{6}\right\rfloor = 65$|$305-65\times2 = 174$|
    |F|$\left\lfloor\frac{198}{6}\right\rfloor = 33$|$174-33\times3 = 75$|
    |:material-alert: We used up all demand but there are 75 empty seats. Insufficient demand! {: colspan=3} |

    What about 5 flights per day?

    |Seat Class|Seats|Seats to fill|
    |-|-|-|
    |Y|$\left\lfloor\frac{1779}{5}\right\rfloor = 355$|$600-355 = 245$|
    |J|$\left\lfloor\frac{395}{5}\right\rfloor = 79$|$245-79\times2 = 87$|
    |F|$\left\lfloor\frac{198}{5}\right\rfloor = 39$|$87-39\times3 = -30$|
    |:simple-ticktick: There are more demand than there are seats to fill. So, fill the remaining seats from J. {: colspan=3} |
    |F\*|$\frac{87}{3}=29$|0|

    (Y, J, F*) is the optimal configuration: 355Y, 79J, 29F.

    And 3 flights per day?

    |Seat Class|Seats|Seats to fill|
    |-|-|-|
    |Y|$\left\lfloor\frac{1779}{3}\right\rfloor = 593$|$600-593 = 7$|
    |J|$\left\lfloor\frac{395}{3}\right\rfloor = 131$|$7-131\times2 = -255$|
    |:simple-ticktick: There are more demand than there are seats to fill. So, fill the remaining seats from Y. {: colspan=3} |
    |J\*|$\frac{7}{2}=3$|0|
    |F\*|0|0|

    (Y, J\*, F\*) is the optimal configuration: 593Y, 3J, 0F.

    \* means it is being limited by the capacity constraint.

Above 5000km, there are practically [no difference in profits](#intermediate) between seat orders (<5%).
Below it, use FJY. See [the formulae](../formulae.md#pax-seat-ordering) for more info.