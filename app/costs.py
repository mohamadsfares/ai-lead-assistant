PRICE_INPUT_PER_M = 0.10
PRICE_OUTPUT_PER_M = 0.50


def estimate_cost(input_tokens, output_tokens):
    return (input_tokens * PRICE_INPUT_PER_M + output_tokens * PRICE_OUTPUT_PER_M) / 1_000_000