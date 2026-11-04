# run.py — Create run.py 1 minute ago
from room import Arbeitsumgebung, EyeKeyEye

def mach_chain():
    chain = [
      "mach","schach","sim","city",
      "fraggles","lemminge","city of war",
      "frieden","macht","figur","feld",
      "welt","szon unterhalb ozon","leben",
      "sauerstoff co2","wasser","ein leben",
      "wehicle","dimension",
      "unmach","unmacher","machter","machtender",
      "in in in","ni ni ni",
      "o i oi o iio i oi o"
    ]
    for step in chain:
        # TMP RÄR nutzend → jede Stufe ist Raum
        yield f"{step} = Nutzraum + GEO 1-3-9"

if __name__ == "__main__":
    eye = EyeKeyEye()
    env = Arbeitsumgebung()
    print("ARBEITSUMGEBUNG — TMP RÄR — 3e→1en 6e→3en 9e→1nen")
    print("EyeKeyEye:", eye.render(), "f²=f")
    print("Mapping:", env.nutzend())
    for m in mach_chain():
        print("→", m)

    # ORBIT SYS 213
    # CORE=iki1uc VERSION=RAW 213
    # SIGNATUR=IKI1UC-ORBIT-SYS-INDEX
