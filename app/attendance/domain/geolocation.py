"""Value Object para geolocalización"""
from dataclasses import dataclass
from math import radians, sin, cos, sqrt, atan2

@dataclass(frozen=True)
class Geolocation:
    """Value Object inmutable para coordenadas geográficas"""
    latitude: float
    longitude: float
    accuracy: float = 10.0  # Precisión en metros

    def __post_init__(self):
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitud debe estar entre -90 y 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitud debe estar entre -180 y 180")
        if self.accuracy < 0:
            raise ValueError("Precisión no puede ser negativa")

    def distance_to(self, other: "Geolocation") -> float:
        """
        Calcula la distancia en metros usando la fórmula de Haversine.

        Args:
            other: Otra ubicación

        Returns:
            Distancia en metros
        """
        R = 6371000  # Radio de la Tierra en metros

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c

    def is_within_radius(self, center: "Geolocation", radius_meters: float) -> bool:
        """
        Verifica si esta ubicación está dentro del radio especificado.

        Args:
            center: Centro del área permitida
            radius_meters: Radio permitido en metros

        Returns:
            True si está dentro del radio
        """
        distance = self.distance_to(center)
        # Considerar también la precisión del GPS
        tolerance = self.accuracy + center.accuracy
        return distance <= (radius_meters + tolerance)