# cargo config
Let $C$ be the capacity of the cargo aircraft, $k$ be the training multiplier, $D$ be the demand, $n$ be the number of trips per day
$$:
C_L=0.7k_LC\\
Y_L=\frac{D_L/n}{C_L} \\
Y_H=1-Y_L \\
$$

It is only valid when when number of trips per day $n$ is:
$$
\begin{align*}
D_H/n&\ge C_HY_H \\
D_H/n&\ge k_HC(1-\frac{D_L/n}{0.7k_LC}) \\
\frac{1}{n}(D_H+\frac{k_HD_L}{0.7k_L}) &\ge k_HC\\
n&\le \frac{D_H+\frac{k_H}{0.7k_L}D_L}{k_HC} \approx \frac{D_H+\frac{D_L}{0.7}}{C}
\end{align*}
$$