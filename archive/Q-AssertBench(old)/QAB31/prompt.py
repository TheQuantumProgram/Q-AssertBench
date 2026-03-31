class PromptQAB31:
    text = """
This quantum program implements Grover's algorithm over a 15-qubit search space.
A target bitstring is embedded in the oracle, and the circuit applies several rounds
of amplification to increase its measurement probability.

Add a diagnostic assertion that checks whether the target bitstring is sufficiently amplified
in the final output distribution. The assertion should confirm that this target state
stands out from the rest and appears significantly more frequently than other states.

Output the complete modified program with the assertion included. No explanations, no comments.
"""
