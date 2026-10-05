"""Mapa (folium) da localização do IP."""
import requests

OUT_DEFAULT = "mapa_ip.html"


def create_map(latitude: float, longitude: float,
               out_path: str = OUT_DEFAULT, zoom: int = 10) -> str:
    """Gera um mapa HTML com marcador verde na coordenada."""
    import folium
    mapa = folium.Map(location=[latitude, longitude], zoom_start=zoom)
    folium.Marker(
        [latitude, longitude],
        popup=f"{latitude}, {longitude}",
        icon=folium.Icon(color="green", icon="info-sign"),
    ).add_to(mapa)
    mapa.save(out_path)
    return out_path


def map_from_ipwho(info: dict, out_path: str = OUT_DEFAULT):
    """Mapa usando lat/lon devolvidas pelo ipwho.is."""
    if not info or "latitude" not in info or "longitude" not in info:
        return None
    return create_map(float(info["latitude"]), float(info["longitude"]), out_path)


def own_public_location() -> tuple:
    """Localização do PRÓPRIO IP público (ipify + ipinfo) — fallback."""
    ip = requests.get("https://api.ipify.org", timeout=10).text
    data = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10).json()
    lat, lon = data["loc"].split(",")
    return float(lat), float(lon)


def map_own_ip(out_path: str = OUT_DEFAULT) -> str:
    lat, lon = own_public_location()
    return create_map(lat, lon, out_path)
