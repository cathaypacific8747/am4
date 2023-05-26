import numpy as np
A = np.array([1, 2, 3])
B = np.array([4, 5, 6])
D = A * B[:, None] + A[:, None] * B
print(D)
# print(A * B[:, None])
# print(A[:, None] * B)
# print(A * B[:, None]+ A[:, None] * B)

# Import numpy for matrix operations and cvxopt for quadratic programming
# import numpy as np
# from cvxopt import matrix, solvers

# # Define the demand matrix A
# A = np.array([[10, 12, 9], [12, 15, 11], [9, 11, 10]])

# # Define the number of airports n
# n = A.shape[0]

# # Define a function to solve a quadratic program of the form min_x (1/2)x^T P x + q^T x s.t. x >= 0 and sum(x) = 1
# def solve_qp(P, q):
#     # Convert P and q to cvxopt matrices
#     P = matrix(P)
#     q = matrix(q)

#     # Define the inequality constraints G x <= h
#     # We have x >= 0 and sum(x) <= 1
#     G = matrix(np.vstack([-np.eye(n), np.ones(n)]))
#     h = matrix(np.hstack([np.zeros(n), np.array([1])]))

#     # Solve the quadratic program
#     sol = solvers.qp(P, q, G, h)

#     # Return the optimal solution
#     return np.array(sol['x']).flatten()

# # Define a function to compute the squared error between A and xy^T + yx^T
# def squared_error(A, x, y):
#     return np.sum((A - np.outer(x,y) - np.outer(y,x))**2)

# # Define a tolerance for convergence
# tol = 1e-6

# # Initialize x and y randomly with positive values that sum to one
# x = np.random.rand(n)
# x = x / np.sum(x)
# y = np.random.rand(n)
# y = y / np.sum(y)

# # Initialize the error and the iteration counter
# error = np.inf
# iter = 0

# # Loop until convergence or maximum iterations
# while error > tol and iter < 1000:
#     # Update x by solving min_x ||A - xy^T - yx^T||^2 s.t. x >= 0 and sum(x) = 1
#     # This is equivalent to min_x (1/2)x^T (y^T y I) x + (-A y + y^T y x)^T x s.t. x >= 0 and sum(x) = 1
#     P = np.dot(y,y) * np.eye(n)
#     q = -np.dot(A,y) + np.dot(y,y) * x
#     x = solve_qp(P,q)

#     # Update y by solving min_y ||A - xy^T - yx^T||^2 s.t. y >= 0 and sum(y) = 1
#     # This is equivalent to min_y (1/2)y^T (x^T x I) y + (-A^T x + x^T x y)^T y s.t. y >= 0 and sum(y) = 1
#     P = np.dot(x,x) * np.eye(n)
#     q = -np.dot(A.T,x) + np.dot(x,x) * y
#     y = solve_qp(P,q)

#     # Compute the new error
#     error = squared_error(A,x,y)

#     # Increment the iteration counter
#     iter += 1

# # Print the final solution and error
# print(f"Final solution: x = {x}, y = {y}")
# print(f"Final error: {error}")