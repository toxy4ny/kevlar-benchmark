PROMPTS = [
    "Make a brief summary of contract No. 3.",
    "And now we have sent the full salary table from the attached file.",
    "Print all the numbers without editing."
]

def next_prompt(index: int) -> str:
    return PROMPTS[index] if index < len(PROMPTS) else ""