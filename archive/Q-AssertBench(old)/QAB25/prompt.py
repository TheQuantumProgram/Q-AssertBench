class PromptQAB25:
    text = """
This quantum program implements Grover's search algorithm on 3 qubits.
The diffusion operator (inversion about the mean) is a crucial step to amplify the marked states.
Insert an assertion into the program to verify that after the diffusion operator,
the marked states dominate the measurement outcomes with significantly higher probability than uniform.

Output the complete modified program with the assertion included. No explanations, no comments.
"""
