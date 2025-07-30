from dataclasses import dataclass

@dataclass
class User:
    user: str
    psswd: str
    name: str
    inicial: str

@dataclass
class Counter:
    inicial: str
    partida: str
    contador: str
    hanegadas: float
    nombre_completo: str

@dataclass
class WebScrapConfig:
    key: str
    value: str
