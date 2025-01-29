import tiktoken

class TokenEstimator:
    def __init__(self, model="gpt-4"):
        self.encoder = tiktoken.encoding_for_model(model)
        self.words_per_minute = 1000
        self.tokens_per_word = 1.3
        self.max_output_tokens = 4000 if model == "gpt-4" else 2000

    def estimate_conversation_splits(self, total_minutes):
        """
        Estimerer hvor mange deler samtalen må deles inn i basert på lengde.
        """
        total_words = total_minutes * self.words_per_minute
        total_tokens = int(total_words * self.tokens_per_word)

        num_splits = -(-total_tokens // self.max_output_tokens)
        return max(1, num_splits)

    def get_tokens_per_split(self, total_minutes, num_splits):
        """
        Beregner hvor mange tokens hver del bør inneholde.
        """
        total_words = total_minutes * self.words_per_minute
        total_tokens = int(total_words * self.tokens_per_word)
        return total_tokens // num_splits