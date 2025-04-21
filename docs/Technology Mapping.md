# Technology Mapping

Technology Mapping transforms technology-independent logic netlists and expresses it with standard cells in a technology library. 

For example, given a library with an AOI21 cell (AND-OR-invert), we might translate the following technology-independent logic tree on the left to the dependent netlist on the right:
| Technology-Independent  | Technology-Dependent |
| :----------------: | :------: |
| <img height="320" alt="Tech Ind Mapping" src="https://github.com/user-attachments/assets/c26f4300-404e-4657-af5f-971d3e9244cb" /> | <img height="320" alt="Tech Dep Mapping" src="https://github.com/user-attachments/assets/91c7dfe6-e3a6-4c33-8f0a-fa245bdace8f"> |

## Technology Library

A technology library specifies a list of cells availble in the library, their logic function, their area/timing cost, along with a list of atomic patterns. 
For example: A simple technology library with just inverters and NANDs will contain the following information:

<img width="300" alt="Tech Lib" src="https://github.com/user-attachments/assets/93e9d7f2-8261-400d-8d79-83f232fa0797" />

## Optimal Tree Covering

Given a boolean network as a subject graph (a DAG of only INVs and 2-input NANDs), we want to find a cover (a collection of pattern DAGs that spans all nodes in the DAG) with the minimum total cost. Unfortunately this problem is NP-hard, so we instead solve for a similar problem by breaking DAGS into trees and separately cover each tree.

<img width="500" alt="Tree Mapping" src="https://github.com/user-attachments/assets/79042c2c-832d-413f-8912-f3cb930f36e6" />

### Pseudocode

```
function TreeCover(T,C):

Input : A tree T representing a logic network, along with a set of cells each with its own pattern trees.
Output: A minimum cost tree constructed with patterns that is logically equivalent with T, and its cost.

min_cost <- Infinity
optimal_cover <- None

for each cell c in C do
  for each pattern P of c do
    e_matched <- MatchPattern(T,P,∅)
    if e_matched is None then
      continue
    endif
    cost <- c.cost
    for each matched pair a, b in e_matched do
      if b is a Node then
        tc, tc_cost <- TreeCover(b,C)
        e_matched[a] <- tc
        cost += tc_cost
      endif
    endfor
    if cost < min_cost then
      min_cost <- cost
      optimal_cover <- Build Node with type c and children <- e_matched
    endif

return optimal_cover, min_cost

endfunction
```

```
function MatchPattern(T,P,e):

Input: A tree T, a pattern P, and a matching env e, which consists a map of pattern terminals to tree nodes/terminals,
Output: Null if pattern p does not match with the tree, or an updated env, with any new terminal matches

if T.node_type != P.node_type then
  return None

if size(T.children) != size(P.children) then
  return None

for each child ct of T, and the corresponding child cp of P do
  if cp is a terminal then
    if e does not contain a mapping for ct then
      e[cp] <- ct
    else if e contains e[ct] != cp
      return None
    endif
  else if cp is a node then
    e_matched <- MatchPattern(ct, cp, copy(e))
    if e_matched is None then
      return None
    else
      e <- union(e,e_matched)
    endif
  endif
endfor

endfunction
  

```

