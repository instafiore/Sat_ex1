#!/usr/bin/python3
from typing import List
from pysat.formula import CNF
from pysat.solvers import Solver

# utility functions
# --------------------------------------START----------------------------------------

def decode_lit(l, n):
  l = abs(l)
  return f"{((l-1) % (n*n)) // n + 1}:{(l-1) % n + 1}:{(l-1) // (n*n) + 1}"

def print_chessboard(answer):
    '''
    This prints the answer in a pretty way.
    Also checking the correctnes of it
    '''
    print("Chessboard")
    n = len(answer)
    count = 0
    for i in range(n):
        for j in range(n):
            queen = None
            for q in range(n):
                assert not answer[i][j][q] is None
                if answer[i][j][q]:
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

def from_model_to_answer(model: List[int], N) -> List[List[List[bool]]]:
    answer = [[[None for q in range(N) ] for j in range(N)] for i in range(N)]

    for l in model:
        sign = l > 0
        split = decode_lit(l, N).split(":")
        i = int(split[0])
        j = int(split[1])
        q = int(split[2])
        answer[i-1][j-1][q-1] = sign

    return answer

def convert_cnf_to_str(cnf: CNF) -> str:
    cnf_str = ""

    for clause in cnf.clauses:
        clause_str = " ".join(map(str, clause)) + " 0\n"
        cnf_str += clause_str
    return cnf_str
    
# ---------------------------------------END----------------------------------------

def queens(N: int) -> str:
    '''
    input: integer N that specifies the number of queens
    output: str encoding the N queens problem in a DIMACS format
    note: this encoding is trying to use as few variables as possible
    '''

    assert N > 3

    # Generation variables
    # For each square of the chessboard we have the variable xij
    # semantic: xijq = T iff in that cell is placed the q-th queen for all i,j,q = 0,...,N
    x = [[[q*N*N+i*N+j+1 for q in range(N) ] for j in range(N)] for i in range(N)]
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

    # at most one constraint: each queen has to be placed in at most one square
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
    # for each column j and for each queen q:
    #   (x1jq V ... V xnjq) -> for all queen k != q (!X1jk ^ ... ^ !XNjk) 
    cnf_queen_column = []
    for j in range(N):
        for q in range(N):
            for i1 in range(N):
               # avoid repeated clauses
               for k in range(q+1, N):
                for i2 in range(N):
                    clause = [-x[i1][j][q], -x[i2][j][k]]
                    cnf_queen_column.append(clause)
    cnf += cnf_queen_column

    # pretty_cnf(cnf_queen_column, N)

    # no two queen in a row -> each row has to have at most 1 queen
    # for each row i and for each queen q:
    #   (xi1q V ... V xiNq) -> for all queen k != q (!Xi1k ^ ... ^ !XiNk) 
    cnf_queen_rows = []
    for i in range(N):
        for q in range(N):
            for j1 in range(N):
               # avoid repeated clauses
               for k in range(q+1, N):
                for j2 in range(N):
                    clause = [-x[i][j1][q], -x[i][j2][k]]
                    cnf_queen_rows.append(clause)
    cnf += cnf_queen_rows
               
    # pretty_cnf(cnf_queen_rows, N)

    # no two queen in a diagonal -> each diagonal has to have at most 1 queen
    # for each row i and for each queen q:
    #   if for some column j xijq -> for all queen k != q !xldk for some ld s.t
    #   i-j = l-d 
    cnf_queen_diagonal = []
    for i in range(N):
        for q in range(N):
            for j in range(N):
               # avoid repeated clauses
                for k in range(q+1, N):
                    diff = i - j
                    if diff >= 0:
                       l = diff
                       d = 0
                    else:
                       l = 0
                       d = -diff
                    while l < N and d < N:
                        clause = [-x[i][j][q], -x[l][d][k]]
                        cnf_queen_diagonal.append(clause)  
                        l += 1
                        d += 1  
    cnf += cnf_queen_diagonal           

    return cnf

def write_cnf(cnf: CNF) -> None:
    '''
    input: cnf formula
    behavior: writes in the DIMACS format the cnf in input in the file output.cnf
    '''
    cnf_str = convert_cnf_to_str(cnf=cnf)

    with open("output.cnf", "w") as f:
        f.write("p cnf {} {}\n".format(cnf.nv, len(cnf.clauses)))
        f.write(cnf_str)

def debug():

    # number of queen
    N = 4
    cnf_list = queens(4)

    answers = []
    added_clauses = []
    while True:
        cnf = CNF(from_clauses=cnf_list+added_clauses)
        solver = Solver(bootstrap_with=cnf)
        if (not solver.solve()):
            break
        model = solver.get_model()
        answer = from_model_to_answer(model, N)
        answers.append(answer)
        new_clause = [-l for l in model]
        added_clauses.append(new_clause)
    
    print(f"There are {len(answers)} different answers")
    for answer in answers:
        print_chessboard(answer=answer)

debug()

