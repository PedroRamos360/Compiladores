def read_code_file(name):
    with open(f"./codigos/{name}", "r", encoding="utf-8") as file:
        code = file.read()
    return code
