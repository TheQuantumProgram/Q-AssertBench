class PromptQAB20:
    text = """
This quantum program demonstrates the construction of a periodic oracle with hidden period a.
The oracle maps input qubits to output qubits such that f(x) = f(x XOR a).
Insert an assertion into the program to verify that for each input x, the output is the same
as for its paired input x XOR a.

Output the complete modified program with the assertion included. No explanations.
"""

