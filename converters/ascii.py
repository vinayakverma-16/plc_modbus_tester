class ASCIIConverter:
    @staticmethod
    def text_to_hex(text: str) -> str:
        return " ".join(f"{ord(c):02X}" for c in text)

    @staticmethod
    def hex_to_text(hex_str: str) -> str:
        hex_str = hex_str.replace(" ", "")
        chars = []
        for i in range(0, len(hex_str), 2):
            code = int(hex_str[i:i+2], 16)
            if 32 <= code <= 126:
                chars.append(chr(code))
            else:
                chars.append(".")
        return "".join(chars)

    @staticmethod
    def text_to_bin(text: str) -> str:
        return " ".join(f"{ord(c):08b}" for c in text)

    @staticmethod
    def bin_to_text(bin_str: str) -> str:
        bin_str = bin_str.replace(" ", "")
        chars = []
        for i in range(0, len(bin_str), 8):
            code = int(bin_str[i:i+8], 2)
            if 32 <= code <= 126:
                chars.append(chr(code))
            else:
                chars.append(".")
        return "".join(chars)

    @staticmethod
    def text_to_utf8_hex(text: str) -> str:
        encoded = text.encode("utf-8")
        return " ".join(f"{b:02X}" for b in encoded)

    @staticmethod
    def utf8_hex_to_text(hex_str: str) -> str:
        hex_str = hex_str.replace(" ", "")
        try:
            data = bytes(int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2))
            return data.decode("utf-8", errors="replace")
        except Exception:
            return "Error"
