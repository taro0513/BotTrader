class Utils:
    @staticmethod
    def key_in_text(keys: list, text: str) -> bool:
        for key in keys:
            if key in text.lower():
                return True
        return False