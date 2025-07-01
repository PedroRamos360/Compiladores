def read_code_file(name: str, folder: str = "./codigos") -> str:
    with open(f"{folder}/{name}", "r", encoding="utf-8") as file:
        code = file.read()
    return code
