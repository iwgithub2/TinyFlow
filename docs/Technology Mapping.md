# Technology Mapping

Technology Mapping transforms technology-independent logic netlists and expresses it with standard cells in a technology library. 

For example, given a library with an AOI21 cell (AND-OR-invert), we might translate the following technology-independent logic tree on the left to the dependent netlist on the right:
| Technology-Independent  | Technology-Dependent |
| :---------------- | :------: |
| ![db_parsed](https://github.com/user-attachments/assets/c26f4300-404e-4657-af5f-971d3e9244cb) | ![db_mapped](https://github.com/user-attachments/assets/91c7dfe6-e3a6-4c33-8f0a-fa245bdace8f) |

## Technology Library

A technology library specifies a list of cells availble in the library, their logic function, their area/timing cost, along with a list of atomic patterns. 
For example: A simple technology library with just inverters and NANDs will contain the following information:

<img width="300" alt="Tech Lib" src="https://github.com/user-attachments/assets/93e9d7f2-8261-400d-8d79-83f232fa0797" />

## Optimal Tree Covering

