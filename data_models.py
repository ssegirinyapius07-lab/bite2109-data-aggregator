from dataclasses import dataclass


@dataclass(slots=True)
class Product:
    id: int
    name: str
    price: float
    category: str
    avg_score: float = 0.0
    review_count: int = 0