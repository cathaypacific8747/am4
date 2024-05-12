> "The purpose of computing is insight, not numbers." *-- Richard Hamming*

From orbiting planets to subatomic particles, equations have the power to describe and explain many phenomena we experience daily.

As we gaze up at the skies, it's easy to take for granted the intricate dance of physics, economics, and business that makes modern air travel possible. But beneath the surface, a complex web of equations governs every aspect of aviation: from the [lift and drag](https://en.wikipedia.org/wiki/Kutta%E2%80%93Joukowski_theorem) that propel planes through the air, to the delicate balance of [supply and demand that determines ticket prices](https://en.wikipedia.org/wiki/Yield_management), and the [air traffic management techniques](https://en.wikipedia.org/wiki/Braess%27s_paradox) that minimise flight delays. Yet, despite this complexity, there's beauty in the underlying simplicity of the equations that govern it all.

Of course, AM4 is a massive simplification governed by very simple equations - this guide aims to familiarise you with:

- understanding the concept of linear equations
- using regression models to build theories

!!! example "Experimental"
    This guide is a preview and not finalised!

## Easy

We know that ticket prices are typically more expensive for longer routes. But how can we write that as an equation?

There are many ways to write it down, but the simplest way is a *linear* equation, in the form:
$$
y = mx + c
$$
here, $y$ is called the **dependent variable** and $x$ is called the **independent variable**. $m$ and $c$ are **parameters** that we hope to estimate, based on the data we collected.

Multiplying the distance $x$ by some number $m$ and adding some number $c$ will give us ticket price $y$.

Here is what it looks like - try dragging the two dots!

<iframe src="https://www.desmos.com/calculator/dg3cur8f65?embed" width="100%" height="300" frameborder=0></iframe>

Some observations:

- If we *know* the positions of the red and blue dots, namely $(x_1, y_1)$ and $(x_2, y_2)$, it would "lock in" to the singular black line.
- Clicking on any point in the black line will tell us the ticket price $y$ for that distance $x$.
- Moving the points changes $m$ and $c$: for instance, moving blue dot upwards will increase $m$ and decrease $c$.

But how are $m$ and $c$ calculated, and what do they mean?

### Slope $m$

Imagine the line as a hill: $m$ describes how steep that slope is.

For example, $m=2$ means, if you move 1 step to the right, you will ascend 2 steps upwards.

Mathematically, we express slope as:

$$
m = \frac{\text{rise}}{\text{run}} = \frac{\text{2 steps }\uparrow}{\text{1 step }\rightarrow} = 2
$$

rise meaning the change in height $\Delta y$ and run meaning change in lateral distance $\Delta x$.

??? question "Exercise 1: At a distance of 1000km, the ticket price is $\$570$. At a distance of 2000km, the ticket price is $\$970$. What is the slope $m$?"
    
    The horizontal direction is distance $x$, vertical direction is ticket price $y$.

    Slope is how much we ascended (rise, $\Delta y$) divided by how much we moved horizontally (run $\Delta x$):

    $$
    m = \frac{\text{rise}}{\text{run}} = \frac{970 - 570}{2000 - 1000} = \frac{400}{1000} = 0.4.
    $$

    The unit for $m$ is dollars per km.

Intuitively, steeper slopes define how rapidly ticket prices change with a step in distances, which is why it is also commonly referred as the **rate of change** or the [**derivative**](https://en.wikipedia.org/wiki/Derivative).

### Y-intercept $c$

The black line extends across all distances $x$, and when it arrives at zero distance, the ticket price at that point is called the y-intercept.

For example, $c = 0$ means the ticket price $y$ is $\$0$ when the route distance $x$ is 0 km.

To compute this, we need the generic formula $y=mx+c$, a known slope $m$ and a set of points $(x_0, y_0)$. Rearranging, we get:
$$
c = y_0 - mx_0
$$

??? question "Exercise 2: Continuing on Exercise 1, what is the y-intercept $c$?"

    We know the slope $m=0.4$, and select one point $(1000\text{ km}, \$570)$.

    $$
    c = 570 - 0.4 \times 1000 = 170
    $$

    This means, at a distance of 0km, passengers will have to pay $170.

Intuitively, if we are at an initial elevation $y_0$ and descend the slope by moving left $\leftarrow$ by $x_0$, we arrive at the y-intercept.

### Useful operations

Generally, as long as we have two data points, we can always find $m$ and $c$.

We found them in Exercises 1 and 2, which *transforms* distance $x$ to ticket price $y$.

$$
y=0.4x+170
$$

But we can also do the **inverse**, transforming ticket price $y$ back into distance $x$.

??? question "Exercise 3: Using the equation above, find the distance when the ticket price is $\$6900$."
    Rearranging and substituting $y=6900$:
    
    $$
    \begin{align*}
    y &= 0.4x + 170 \\
    y - 170 &= 0.4x \\
    x &= \frac{y - 170}{0.4} = \frac{6730}{0.4} = 16825\text{ km}
    \end{align*}
    $$

Let's try another practice:

??? question "Exercise 4: I gathered some data on business class ticket prices. When the distance is 1300km, the ticket price is $\$1600$. When the distance is 4200km, the ticket price is $\$3920$. What is the distance I need to fly for a ticket price of $\$10000$?"

    We are given two points: (1000, 1600) and (4200, 3920).
    
    The equation $y=mx+c$ needs $m$ and $c$ to be found:

    $$
    \begin{align*}
        m &= \frac{y_2-y_1}{x_2-x_1} \\
        &= \frac{3920 - 1600}{4200 - 1300} \\
        &= 2320/2900 = 0.8
    \end{align*}
    $$
    
    $$
    \begin{align*}
        c &= y_0 - mx_0 \\
        &= 1600 - 0.8 \times 1300 = 560
    \end{align*}
    $$

    So the equation is $y=0.8x+560$ and we need to rearrange to solve x:

    $$
    x = \frac{y-560}{0.8} = \frac{10000-560}{0.8} = 11800\text{ km}
    $$

    Notice that the slope $0.8$ is twice the economy class of $0.4$, suggesting that the business class ticket prices grow twice as fast as economy classes!

??? question "Exercise 5: We've found the economy and business class ticket price equations in Exercises 2 and 4. But consider: 1 business class takes up 2 economy class tickets. Which gives more profit per 'space'?"

    Dividing the business class ticket price by 2:
    
    $$
    \begin{align*}
        y_{\text{economy}} &= 0.4x+170 \\
        y_{\text{business}} &= \frac{0.8x+560}{2} = 0.4x+280
    \end{align*}
    $$

    Here, the slope $m$ of the economy and business class ticket prices are both $0.4$ - meaning they grow at the same rate.

    The difference lies in the y-intercept $c$: at a distance of zero, business class pays $\$280$ while economy class pays $\$170$. So business class will always overperform economy class.

### Summary

- A linear function $y=mx+c$ describes the relationship between $y$ and $x$
- slope $m$ and y-intercept $c$ are calculated from two points, $(x_0, y_0)$ and $(x_1, y_1)$:
    - $m = \frac{\text{rise}}{\text{run}} = \frac{y_1-y_0}{x_1-x_0}$ describes the rate of change of the slope
    - $c = y_0-mx_0$ is the value $y$ when $x=0$


## Intermediate

In the previous section, we know a linear equation can be written in the form $y=mx+c$. We could certainly find $m$ and $c$ from 2 points, but AM4 often gives you a *noisy* version of the data.

For example, departing a plane contributes to your alliance - but that value is randomly offset by some value, meaning if we had just used $m=\frac{y_1-y_0}{x_1-x_0}$, it would yield different results every single time. We want generalised equations that best capture the relationship.

Fortunately, we can gather data points, and use [**regression**](https://en.wikipedia.org/wiki/Ordinary_least_squares) to find the **line of best fit**.

In Excel, you can always create a scatter plot for a dataset, then quickly find the optimum $m$ and $c$. Python can do it similarly with one line of code. But it is always fun to understand how it works behind the hood - it is yet another simple equation!

I assume you have some basic knowledge of linear algebra (I highly recommend the [3b1b series](https://www.3blue1brown.com/topics/linear-algebra) if you are not familiar with it)

### Regression

Say we have three data points $A(1,1)$, $B(2, 3)$, $C(3, 2)$ and assume some linear line $y=mx+c$ that passes through them.

We have:

$$
\begin{align*}
1 &= m\times1+c \\
3 &= m\times2+c \\
2 &= m\times3+c
\end{align*}
$$

The goal is to find $m$ and $c$ that satisfy all three equations.

We can try to calculate the slope for the first two points: $m = \frac{3-1}{2-1} = 2$, and y-intercept $c = 1-2\times1 = -1$. But substitute that into the third equation: $2\times3 - 1 = 5$, which is clearly not $2$ - we call this [**inconsistent**](https://en.wikipedia.org/wiki/Consistent_and_inconsistent_equations).

In fact, we have 3 linearly independent equations and 2 unknowns - no combination of $m$ and $c$ will possibly satisfy all three equations. We call this an **overdetermined** system of equations because there are more equations than unknowns.

#### Matrices

It is convenient to rewrite the equations in matrix form:

$$
\underbrace{
\begin{bmatrix}
1 & 1 \\
1 & 2 \\
1 & 3
\end{bmatrix}
}_{\mathbf{A}}
\underbrace{
\begin{bmatrix}
m \\
c
\end{bmatrix}
}_{\mathbf{x}}
=
\underbrace{
\begin{bmatrix}
1 \\
3 \\
2
\end{bmatrix}
}_{\mathbf{b}}
$$

Intuitively, multiplying $\mathbf{A}$ by $\mathbf{x}$ effectively *applies* a 3D transformation to a 2D point, to get the final point $\mathbf{b}$. Now what does $\mathbf{A}$ physically mean?

There are two columns in this matrix: $[1 1 1]^\top$ and $[1 2 3]^\top$. The first column tells me that (1, 0) in 2D space should move to (1, 1, 1) in 3D space. Similarly, (0, 1) moves to (1, 2, 3). This matrix essentially prescribes *how* to transform from our inputs to our outputs (see 3b1b's visualisation [here](https://www.youtube.com/watch?v=v8VSDg_WQlA)).

So, the question is - what point $\mathbf{x}(m, c)$ in the input space, after the 3D transformation, will get me to $\mathbf{b}(1, 3, 2)$?

#### Inverse

Well, what if we could *invert* the $\mathbf{A}$ transformation on $\mathbf{x}$? If we multiply can both sides by $\mathbf{A}^{-1}$, we would get $\mathbf{A}^{-1}\mathbf{A}\mathbf{x}=\mathbf{A}^{-1}\mathbf{b}$. (notice that $\mathbf{A}^{-1}\mathbf{A}$ performs the transformation then undo it, so effectively it does nothing: the [**identity matrix**](https://en.wikipedia.org/wiki/Identity_matrix#Properties) $\mathbf{I}$). Cancelling, we have the solution $\mathbf{x}=\mathbf{A}^{-1}\mathbf{b}$!

But here's the thing, matrices are conventionally only [**invertible**](https://en.wikipedia.org/wiki/Invertible_matrix) if the number of rows matches the number of columns. A $3\times 2$ matrix $\mathbf{A}$ with full column rank (i.e. all columns are linearly independent) defines a 2D "sheet of paper" in 3D space!

#### Normal equation

Now, what can we do instead? We can find the **left inverse** of $\mathbf{A}$ instead. We can take the transpose of $\mathbf{A}$ on both sides of the equation:

$$
\mathbf{A}^\top \mathbf{A} \mathbf{x} = \mathbf{A}^\top \mathbf{b}
$$

By taking the transpose of $\mathbf{A}$, we're essentially "flipping" the matrix, so that the rows become columns and vice versa. This creates a new matrix $\mathbf{A}^\top \mathbf{A}$, which is symmetric and, more importantly, invertible!

Now, we can multiply both sides by the inverse of $\mathbf{A}^\top \mathbf{A}$, which is denoted as $(\mathbf{A}^\top \mathbf{A})^{-1}$. This gives us:

$$
\mathbf{x} = \underbrace{(\mathbf{A}^\top \mathbf{A})^{-1} \mathbf{A}^\top}_{\text{left inverse }\mathbf{A}^{-1}}\mathbf{b}
$$

This is known as the **normal equation**, and it provides the best possible approximation of the solution $\mathbf{x}$ in the sense of [minimizing the least squares error](https://en.wikipedia.org/wiki/Linear_least_squares#Formulations_for_Linear_Regression).

___

Now let's return to our example, with $\mathbf{A} = \begin{bmatrix}1 & 1 \\1 & 2 \\1 & 3\end{bmatrix}$ and find its left inverse:

- Find $\mathbf{A}^\top \mathbf{A}$, the **Gram matrix**:
   
$$
\begin{align*}
\begin{bmatrix}1 & 1 & 1 \\ 1 & 2 & 3\end{bmatrix}\begin{bmatrix}1 & 1 \\1 & 2 \\1 & 3\end{bmatrix}&=\begin{bmatrix}1(1)+1(1)+1(1) & 1(1)+1(2)+1(3) \\ 1(1)+2(1)+3(1) & 1(1)+2(2)+3(3)\end{bmatrix} \\
&= \begin{bmatrix}
    3 & 6 \\
    6 & 14
\end{bmatrix}
\end{align*}
$$

- Take its inverse, recalling the formula for $2\times2$ matrices, using its [determinant](https://www.3blue1brown.com/lessons/determinant) $\text{det}(\mathbf{A})$:

$$
\begin{bmatrix}
a & b \\
c & d
\end{bmatrix}^{-1} = \frac{1}{ad - bc}\begin{bmatrix}
d & -b \\
-c & a
\end{bmatrix}
$$

$$
(\mathbf{A}^\top \mathbf{A})^{-1} = \frac{1}{3(14) - 6(6)} \begin{bmatrix}
14 & -6 \\
-6 & 3
\end{bmatrix} = \frac{1}{6} \begin{bmatrix}
14 & -6 \\
-6 & 3
\end{bmatrix} = \begin{bmatrix}
\frac{7}{3} & -1 \\
-1 & \frac{1}{2}
\end{bmatrix}
$$

- Now, multiply that by $A^\top$ to get $\mathbf{A}^{-1}$:

$$
(\mathbf{A}^\top \mathbf{A})^{-1} \mathbf{A}^\top = \begin{bmatrix}
\frac{7}{3} & -1 \\
-1 & \frac{1}{2}
\end{bmatrix} \begin{bmatrix}
1 & 1 & 1 \\
1 & 2 & 3
\end{bmatrix} = \begin{bmatrix}
-\frac{1}{3} & \frac{1}{3} & 1 \\
\frac{1}{2} & 0 & -\frac{1}{2}
\end{bmatrix}
$$

- finally, multiply it with $\mathbf{b}=\begin{bmatrix}1\\3\\2\end{bmatrix}$:

$$
\mathbf{x} = \mathbf{A}^{-1} \mathbf{b} = \begin{bmatrix}
\frac{4}{3} & \frac{1}{3} & -\frac{2}{3} \\
-\frac{1}{2} & 0 & \frac{1}{2}
\end{bmatrix} \begin{bmatrix}
1 \\
3 \\
2
\end{bmatrix} = \begin{bmatrix}
1 \\
\frac{1}{2}
\end{bmatrix}
$$

The line of best fit is thus $y=x+\frac{1}{2}$.

??? question "Exercise 6: Implement the normal equation in Python, writing a function that takes in a list of $x$ and corresponding $y$, returning $m$ and $c$. Use `numpy`."

    Recall $\mathbf{x}=(\mathbf{A}^\top\mathbf{A})^{-1}\mathbf{A}^\top\mathbf{b}$.

    ```py
    --8<-- "formulae.py:normal-eq"
    ```

    Verifying that our implementation is indeed correct:
    ```py
    --8<-- "formulae.py:normal-eq-output"
    ```

### Multiple Linear Regression

The normal equation can also be extended to perform **multiple linear regression**, i.e. $y=\beta_0 x_0 + \beta_1 x_1 + ... + \beta_m x_m$ with $m$ predictor variables.

$$
\mathbf{x}=(\mathbf{A}^\top\mathbf{A})^{-1}\mathbf{A}^\top\mathbf{b}
$$

$\mathbf{A}$ is called the **design matrix** with size $n \times m+1$. It would look like:

$$
\underbrace{
    \begin{bmatrix}
    \rule[-1ex]{0.5pt}{2.5ex} & \rule[-1ex]{0.5pt}{2.5ex} & \rule[-1ex]{0.5pt}{2.5ex} & & \rule[-1ex]{0.5pt}{2.5ex} \\
    1 & x_1 & x_2 & \ldots & x_m \\
    \rule[-1ex]{0.5pt}{2.5ex} & \rule[-1ex]{0.5pt}{2.5ex} & \rule[-1ex]{0.5pt}{2.5ex} & & \rule[-1ex]{0.5pt}{2.5ex} \\
    \end{bmatrix}
}_{\text{m\text{ predictor variables}}}
$$

For example, if we *hypothesise* the contribution to be some linear combination of distance and CI, and want to figure out the exact formula, we should:

1. Write the equation as: $\text{contribution} = \beta_0 + \beta_1 \cdot \text{distance} + \beta_2 \cdot \text{CI}$,
2. Collect samples of $(\text{distance}, \text{CI}, \text{contribution})$ and rewrite it in the design matrix $\mathbf{A}$ and true values $\mathbf{b}$,
3. Evaluate the normal equation and solving for $\mathbf{x}$ will give $\begin{bmatrix}\beta_0 \\ \beta_1 \\ \beta_2\end{bmatrix}$.

### Summary

Most formulae in the game can be described as:

- $y=\beta_0 + \beta_1 x_1 + \ldots + \beta_m x_m$
- we should collect many sets of $(x_1, \dots, x_m, y)$ samples and compute $(\mathbf{A}^\top\mathbf{A})^{-1}\mathbf{A}^\top\mathbf{b}$
    - Excel, Desmos and `numpy` are great tools to do it automatically
- usually, $y$ is dependent on only one or two variables
    - Occam's razor suggests equations should be as simple as possible.
    - if you perform MLR, the $\beta$ for redundant independent variables should be zero.

Formulae can also sometimes be **non-linear** (e.g. contribution), possibly in the form $z=xy$ or $e^{x}\sin(y)$. In that case, when collecting data, we should *isolate* one variable and investigate relationships independently.