class AlapOsztaly:
    def __init__(self, nev, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Továbbítja a paramétereket a többi osztályhoz
        self.nev = nev

    def koszont(self):
        return f"Hello, {self.nev}!"

# Mixin osztályok
class LogolasMixin:
    def log(self, uzenet):
        print(f"[LOG] {uzenet}")

class SzamlaloMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # FONTOS: Ez biztosítja az MRO-n keresztüli meghívást
        self.szamlalo = 0

    def noveles(self):
        self.szamlalo += 1
        return self.szamlalo

# Egyedi osztály több öröklődéssel
class EgyediOsztaly(AlapOsztaly, LogolasMixin, SzamlaloMixin):
    def __init__(self, nev, extra_adat, *args, **kwargs):
        super().__init__(nev, *args, **kwargs)  # Továbbadja az összes argumentumot
        self.extra_adat = extra_adat

    def extra_funkcio(self):
        self.log(f"Extra funkció hívása: {self.extra_adat}")
        return f"Extra adat: {self.extra_adat}"

# Használat
obj = EgyediOsztaly("Anna", "Speciális adatok")
print(obj.koszont())  # "Hello, Anna!"
print(obj.extra_funkcio())  # Logol és visszaad egy szöveget
print(obj.noveles())  # 1
print(obj.noveles())  # 2
print(EgyediOsztaly.__mro__)
