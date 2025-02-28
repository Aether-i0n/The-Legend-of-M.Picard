class Attribut:
    def __init__(self, nom: str, type: str, clé_primaire: bool):
        self.nom = nom
        self.type = type
        self.clé_primaire = clé_primaire

def sql_en_format(sql: str):
    
    lignes = sql.split("\n")
    attributs: list[Attribut] = []
    refs: list[tuple[tuple[str, str], tuple[str, str]]] = []
    """ refs: [((str, str), (str, str))] """

    types = {
        "TEXT": "text",
        "INT": "integer",
        "FLOAT": "float"
    }

    table = lignes[0].split()[2].replace('"', "")

    for ligne in lignes[1:-1]:
        if ligne[0] == "-":
            continue
        mots = ligne.split()
        if mots[0] == "PRIMARY":

            clés = []
            for mot in mots[2:]:
                clés.append(mot.replace(",", "").replace("(", "").replace(")", ""))
            
            for attribut in attributs:
                if attribut.nom in clés:
                    attribut.clé_primaire = True
            continue
        
        nom = mots[0].replace('"', "")
        type = types[mots[1].replace(",", "")]
        clé_primaire = False

        if len(mots) > 2:

            if mots[2] == "PRIMARY":
                clé_primaire = True
            
            else:
                parties = mots[3].split("(")
                ref = (parties[0].replace('"', ""), parties[1].replace(",", "")[:-1])
                refs.append(((table, nom), ref))
    
        attributs.append(Attribut(nom, type, clé_primaire))

    format_table = [f"Table {table} {'{'}"]

    for attribut in attributs:
        format_table.append(f"    {attribut.nom} {attribut.type}{' [primary key]' if attribut.clé_primaire else ''}")

    format_table.append("}")

    if len(refs):
        format_table.append("")
    
    for ref in refs:
        format_table.append(f"Ref: {ref[0][0]}.{ref[0][1]} > {ref[1][0]}.{ref[1][1]}")

    return format_table

final = []
with open("Ressources/Bases de Données/instructions.sql", "r") as fichier:
    instructions = fichier.read()
    for instruction in instructions.split("\n\n"):
        if instruction.split()[0] == "INSERT":
            break
        final.extend(sql_en_format(instruction))
        final.append("")

del final[len(final)-1]

print("-"*30)
print("https://dbdiagram.io/d")
print("-"*30)
print("\n".join(final))
print("-"*30)