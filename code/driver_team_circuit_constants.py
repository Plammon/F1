"""Shared 2026 Formula 1 constants used by the apps and prediction engines."""

from __future__ import annotations


F1_2026_GRID = {
    "Red Bull Racing": {
        "Drivers": ["Max Verstappen", "Isack Hadjar"],
        "Engine": "Red Bull Ford",
    },
    "Ferrari": {
        "Drivers": ["Lewis Hamilton", "Charles Leclerc"],
        "Engine": "Ferrari",
    },
    "Mercedes": {
        "Drivers": ["George Russell", "Kimi Antonelli"],
        "Engine": "Mercedes",
    },
    "McLaren": {
        "Drivers": ["Lando Norris", "Oscar Piastri"],
        "Engine": "Mercedes",
    },
    "Aston Martin": {
        "Drivers": ["Fernando Alonso", "Lance Stroll"],
        "Engine": "Honda",
    },
    "Racing Bulls": {
        "Drivers": ["Liam Lawson", "Arvid Lindblad"],
        "Engine": "Red Bull Ford",
    },
    "Cadillac": {
        "Drivers": ["Valtteri Bottas", "Sergio Perez"],
        "Engine": "Cadillac",
    },
    "Alpine": {
        "Drivers": ["Pierre Gasly", "Franco Colapinto"],
        "Engine": "Alpine",
    },
    "Williams": {
        "Drivers": ["Alexander Albon", "Carlos Sainz"],
        "Engine": "Mercedes",
    },
    "Audi": {
        "Drivers": ["Nico Hulkenberg", "Gabriel Bortoleto"],
        "Engine": "Audi",
    },
    "Haas": {
        "Drivers": ["Esteban Ocon", "Oliver Bearman"],
        "Engine": "Ferrari",
    },
}


# The public keys are the circuit names shown in the app. The model aliases map
# those names back to the feature labels used by the qualifying and race models.
F1_2026_TRACKS = {
    "Albert Park": {
        "Round": 1,
        "Event": "Australian Grand Prix",
        "Type": "Street/Hybrid",
        "DNA": "Medium-Speed / Flowing",
        "Qualifying_GP": "Australian Grand Prix",
        "Race_GP": "Albert Park",
    },
    "Shanghai": {
        "Round": 2,
        "Event": "Chinese Grand Prix",
        "Type": "Permanent",
        "DNA": "Front-Limited / Technical",
        "Qualifying_GP": "Chinese Grand Prix",
        "Race_GP": "Shanghai",
    },
    "Suzuka": {
        "Round": 3,
        "Event": "Japanese Grand Prix",
        "Type": "Permanent",
        "DNA": "High-Speed-Flowing / Technical",
        "Qualifying_GP": "Japanese Grand Prix",
        "Race_GP": "Suzuka",
    },
    "Miami": {
        "Round": 4,
        "Event": "Miami Grand Prix",
        "Type": "Street/Hybrid",
        "DNA": "Traction / Long Straights",
        "Qualifying_GP": "Miami Grand Prix",
        "Race_GP": "Miami",
    },
    "Montreal": {
        "Round": 5,
        "Event": "Canadian Grand Prix",
        "Type": "Street/Hybrid",
        "DNA": "Stop-and-Go / Heavy Braking",
        "Qualifying_GP": "Canadian Grand Prix",
        "Race_GP": "Montreal",
    },
    "Monaco": {
        "Round": 6,
        "Event": "Monaco Grand Prix",
        "Type": "Street",
        "DNA": "Low-Speed / Max-Downforce",
        "Qualifying_GP": "Monaco Grand Prix",
        "Race_GP": "Monaco",
    },
    "Barcelona-Catalunya": {
        "Round": 7,
        "Event": "Barcelona-Catalunya Grand Prix",
        "Type": "Permanent",
        "DNA": "Aerodynamic-Efficiency",
        "Qualifying_GP": "Spanish Grand Prix",
        "Race_GP": "Barcelona",
    },
    "Red Bull Ring": {
        "Round": 8,
        "Event": "Austrian Grand Prix",
        "Type": "Permanent",
        "DNA": "Power-Unit / Elevation-Changes",
        "Qualifying_GP": "Austrian Grand Prix",
        "Race_GP": "Red Bull Ring",
    },
    "Silverstone": {
        "Round": 9,
        "Event": "British Grand Prix",
        "Type": "Permanent",
        "DNA": "Ultra-High-Speed / Aero-Load",
        "Qualifying_GP": "British Grand Prix",
        "Race_GP": "Silverstone",
    },
    "Spa": {
        "Round": 10,
        "Event": "Belgian Grand Prix",
        "Type": "Permanent",
        "DNA": "Power-Unit / Long-Straights",
        "Qualifying_GP": "Belgian Grand Prix",
        "Race_GP": "Spa",
    },
    "Hungaroring": {
        "Round": 11,
        "Event": "Hungarian Grand Prix",
        "Type": "Permanent",
        "DNA": "High-Downforce / Slow-Speed",
        "Qualifying_GP": "Hungarian Grand Prix",
        "Race_GP": "Hungarian Grand Prix",
    },
    "Zandvoort": {
        "Round": 12,
        "Event": "Dutch Grand Prix",
        "Type": "Permanent",
        "DNA": "High-Downforce / Banking",
        "Qualifying_GP": "Dutch Grand Prix",
        "Race_GP": "Zandvoort",
    },
    "Monza": {
        "Round": 13,
        "Event": "Italian Grand Prix",
        "Type": "Permanent",
        "DNA": "Top-Speed / Ultra-Low-Drag",
        "Qualifying_GP": "Italian Grand Prix",
        "Race_GP": "Monza",
    },
    "Madrid": {
        "Round": 14,
        "Event": "Spanish Grand Prix",
        "Type": "Street/Hybrid",
        "DNA": "Mixed / Flowing-Esses",
        "Qualifying_GP": "Spanish Grand Prix",
        "Race_GP": "Barcelona",
        "Model_Note": "Madrid is new for 2026, so the model uses the historical Spanish GP as its nearest GP proxy.",
    },
    "Baku": {
        "Round": 15,
        "Event": "Azerbaijan Grand Prix",
        "Type": "Street",
        "DNA": "Top-Speed / 90-Degree-Turns",
        "Qualifying_GP": "Azerbaijan Grand Prix",
        "Race_GP": "Baku",
    },
    "Singapore": {
        "Round": 16,
        "Event": "Singapore Grand Prix",
        "Type": "Street",
        "DNA": "Traction / Humidity / Slow-Speed",
        "Qualifying_GP": "Singapore Grand Prix",
        "Race_GP": "Singapore",
    },
    "COTA": {
        "Round": 17,
        "Event": "United States Grand Prix",
        "Type": "Permanent",
        "DNA": "Mixed / Flowing-Esses",
        "Qualifying_GP": "United States Grand Prix",
        "Race_GP": "COTA",
    },
    "Mexico City": {
        "Round": 18,
        "Event": "Mexico City Grand Prix",
        "Type": "Permanent",
        "DNA": "High-Altitude / Low-Air-Density",
        "Qualifying_GP": "Mexico City Grand Prix",
        "Race_GP": "Mexico City",
    },
    "Interlagos": {
        "Round": 19,
        "Event": "Sao Paulo Grand Prix",
        "Type": "Permanent",
        "DNA": "Elevation / Mixed / Short-Lap",
        "Qualifying_GP": "São Paulo Grand Prix",
        "Race_GP": "São Paulo Grand Prix",
    },
    "Las Vegas": {
        "Round": 20,
        "Event": "Las Vegas Grand Prix",
        "Type": "Street",
        "DNA": "Top-Speed / Low-Tire-Temp",
        "Qualifying_GP": "Las Vegas Grand Prix",
        "Race_GP": "Las Vegas",
    },
    "Lusail": {
        "Round": 21,
        "Event": "Qatar Grand Prix",
        "Type": "Permanent",
        "DNA": "High-Speed / High-G-Force",
        "Qualifying_GP": "Qatar Grand Prix",
        "Race_GP": "Lusail",
    },
    "Yas Marina": {
        "Round": 22,
        "Event": "Abu Dhabi Grand Prix",
        "Type": "Permanent",
        "DNA": "Traction / Technical / Slow-Exit",
        "Qualifying_GP": "Abu Dhabi Grand Prix",
        "Race_GP": "Yas Marina",
    },
}


def get_model_gp_name(track_name: str, mode: str) -> str:
    """Return the GP feature label expected by the selected model."""
    track = F1_2026_TRACKS[track_name]
    return track["Race_GP"] if mode == "race" else track["Qualifying_GP"]
