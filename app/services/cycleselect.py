# service.py
from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode, quote_plus
from typing import List, Tuple, Optional
import math
import random


@dataclass(frozen=True)
class Candidate:
    title: str
    query: str
    maps_url: str
    score: float


def build_maps_search_url(query: str, center: Optional[Tuple[float, float]] = None) -> str:
    """
    Google Maps Search URL（APIキー不要）
    """
    q = query
    if center is not None:
        lat, lng = center
        q = f"{query} near {lat},{lng}"

    params = {"api": "1", "query": q}
    return "https://www.google.com/maps/search/?" + urlencode(params, quote_via=quote_plus)


def km_to_radius_m(distance_km: str) -> int:
    """
    サイクリング用の概算半径[m]
    ループ距離 ≈ 2πr → r ≈ distance/(2π)
    自転車は移動範囲が広いので最低値をやや大きめに
    """
    try:
        lo, hi = distance_km.split("-")
        d_mid = (float(lo) + float(hi)) / 2.0
    except Exception:
        d_mid = 20.0

    r_km = d_mid / (2.0 * math.pi)
    return max(1500, int(r_km * 1000))  # 最低1.5km


def build_keyword_pool(road_type: str) -> List[str]:
    """
    road_type: "flat" or "hills"
    """
    if road_type == "hills":
        return [
            "坂道 サイクリング",
            "ヒルクライム 自転車",
            "峠 サイクリング",
            "アップダウン 多め サイクリング",
            "丘陵 サイクリングコース",
        ]
    # flat
    return [
        "平坦 サイクリングロード",
        "河川敷 サイクリング",
        "海沿い サイクリング",
        "周回 サイクリングコース",
        "信号 少ない サイクリング",
    ]


def build_distance_keywords(distance_km: str) -> List[str]:
    return [
        f"{distance_km}km サイクリング",
        f"{distance_km}km サイクリングコース",
        f"{distance_km}km 自転車 ルート",
    ]


def diversify_queries(
    base_keywords: List[str],
    distance_km: str,
    road_type: str,
    user_location: Optional[str],
) -> List[str]:
    dist_kw = build_distance_keywords(distance_km)

    queries = []
    for bk in base_keywords:
        if user_location:
            queries.append(f"{user_location} {bk}")
            queries.append(f"{user_location} {random.choice(dist_kw)} {bk}")
        else:
            queries.append(f"{random.choice(dist_kw)} {bk}")

    if user_location:
        if road_type == "hills":
            queries.append(f"{user_location} ヒルクライム ルート")
        else:
            queries.append(f"{user_location} フラット ルート 自転車")

    # de-dup
    seen, uniq = set(), []
    for q in queries:
        q2 = " ".join(q.split())
        if q2 not in seen:
            uniq.append(q2)
            seen.add(q2)
    return uniq


def score_query(q: str, road_type: str) -> float:
    score = 0.0
    if road_type == "hills":
        for w in ["坂", "ヒル", "峠", "アップダウン", "丘"]:
            if w in q:
                score += 1.0
    else:
        for w in ["平坦", "河川敷", "海沿い", "周回", "信号"]:
            if w in q:
                score += 1.0
    score += min(1.5, len(q) / 30.0)
    return score


def propose_maps_candidates(
    distance_km: str,
    road_type: str,
    num_results: int = 5,
    user_location: Optional[str] = None,
    center_lat: Optional[float] = None,
    center_lng: Optional[float] = None,
    seed: Optional[int] = None,
) -> List[Candidate]:
    if seed is not None:
        random.seed(seed)

    center = None
    if center_lat is not None and center_lng is not None:
        center = (center_lat, center_lng)

    base_keywords = build_keyword_pool(road_type)
    queries = diversify_queries(base_keywords, distance_km, road_type, user_location)

    scored = [(q, score_query(q, road_type)) for q in queries]
    scored.sort(key=lambda x: x[1], reverse=True)

    head = scored[: max(num_results * 2, 8)]
    if len(head) > num_results:
        chosen = head[:2] + random.sample(head[2:], k=min(num_results - 2, len(head) - 2))
    else:
        chosen = head

    candidates: List[Candidate] = []
    for q, s in chosen[:num_results]:
        url = build_maps_search_url(q, center=center)
        candidates.append(Candidate(title=q, query=q, maps_url=url, score=s))

    candidates.sort(key=lambda c: c.score, reverse=True)
    return candidates
