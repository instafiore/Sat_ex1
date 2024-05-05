#!/usr/bin/python3
from pysat.formula import CNF

def decode_lit(l, n):
  return f"{((l-1) % (n*n)) // n + 1}:{(l-1) % n + 1}:{(l-1) // (n*n) + 1}"

# utility functions
def print_chessboard(x):
    print("Chessboard")
    n = len(x)
    count = 0
    for i in range(n):
        for j in range(n):
            queen = None
            for q in range(n):
                if x[i][j][q]:
                    if not queen is None:
                        raise Exception(f"Two queens in the same position, queens: {queen},{q}")
                    queen = q
                    count += 1
        print(f"{'X' if queen is None else queen}", end=" ")
        print()
    assert count == n


def print_matrix(x):
  print("Matrix")
  n = len(x)
  for q in range(n):
    print(f"Slice {q}")
    for i in range(n):
        for j in range(n):
            print(decode_lit(x[i][j][q],n), end=" ")
        print()

def print_matrix_no_decode(x):
  print("Matrix no decode")
  n = len(x)
  for q in range(n):
    print(f"Slice {q}")
    for i in range(n):
        for j in range(n):
            print(x[i][j][q], end=" ")
        print()

def pretty_cnf(cnf, n):
  print("Clauses")
  for clause in cnf:
    for l in clause:
      nots = ""  
      if l < 0:
        nots = "!"
      print(f"{nots}{decode_lit(abs(l), n)}", end=" ")
    print()

def queens(N: int) -> str:
    '''
    input: integer N that specifies the number of queens
    output: str encoding the N queens problem in a DIMACS format
    note: this encoding is trying to use as few variables as possible
    '''

    # assert N > 3

    # Generation variables
    # For each square of the chessboard we have the variable xij
    # semantic: xijq = T iff in that cell is placed the q-th queen for all i,j,q = 0,...,N
    x = [[[q*N*N+i*N+j+1 for q in range(N) ] for j in range(N)] for i in range(N)]

    print_matrix(x)

    # constraints:
    cnf = []

    # 1. each queen has to be placed in exactly one square
    # at least one constraint: eache queen has to be placed in at least one square
    cnf_atleast_one = []
    for q in range(N):
        cnf_atleast_one_q = []
        for i in range(N):
            for j in range(N):
                # print(x[i][j][q])
                cnf_atleast_one_q.append(x[i][j][q])
        cnf_atleast_one.append(cnf_atleast_one_q)
    cnf += cnf_atleast_one

    # at most one constraint: eache queen has to be placed in at most one square
    cnf_atmost_one = []
    for q in range(N):
        for i in range(N):
            for j in range(N):
               for k in range(i,N):
                  for d in range(N):
                     if k > i or d > j:
                        clause = [-x[i][j][q], -x[k][d][q]]
                        cnf_atmost_one.append(clause)
    cnf += cnf_atmost_one

    # 2. No queen can attack another queen
    # no two queen in a column -> each column has to have at most 1 queen
    for j in range(N):
        for k in range(j+1,N):
            for i in range(N):
               
          


    pretty_cnf(cnf_atmost_one, N)
    




def main():

    queens(2)


main()

