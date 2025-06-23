def read_code_file(name, folder="./codigos"):
    with open(f"{folder}/{name}", "r", encoding="utf-8") as file:
        code = file.read()
    return code
