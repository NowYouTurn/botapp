import pendulum, logging, tempfile
from pathlib import Path
from kerykeion import KrInstance

log = logging.getLogger(__name__)

async def natal_chart_svg(name: str, date: str, time: str, city: str) -> Path:
    dt = pendulum.parse(f"{date}T{time}")
    instance = KrInstance(
        name=name, gender="Neutral", timezone=0,
        birth_date=dt, city=city, country_from_city=city, house_system="placidus"
    )
    path = Path(tempfile.gettempdir()) / f"{name}_{dt.int_timestamp}.svg"
    instance.make_svg(path.as_posix(), draw_aspects=True)
    return path
