# app/services/maps_directions.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DirectionsOptions:
    origin: str
    destination: str
    travel_mode: str          # "BICYCLING"
    provide_alternatives: bool
    avoid_tolls: bool
    avoid_highways: bool

def build_directions_options(origin: str, destination: str, road_type: str) -> DirectionsOptions:
    """
    road_type: "flat" or "hills"
    ※ サイクリングの「坂/平坦」をAPIで厳密に指定するのは難しいので、
      ここでは“それっぽい”制約（高速回避など）に寄せる。
    """
    avoid_highways = True  # 自転車だと基本回避したい
    avoid_tolls = True

    # 坂を選んだ時：完全制御は無理なので、ひとまず回避条件は同じ
    # 平坦：同じ（必要なら後でルート後処理や候補地点戦略で寄せる）
    return DirectionsOptions(
        origin=origin,
        destination=destination,
        travel_mode="BICYCLING",
        provide_alternatives=True,
        avoid_tolls=avoid_tolls,
        avoid_highways=avoid_highways,
    )
