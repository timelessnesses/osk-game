import copy
import dataclasses
import datetime
import enum
import typing

import aiohttp
import dateutil.parser
import orjson
import yarl

from .db import db,connect
from .errors import APIError

complete = {
    "success": None,
    "data": {
        "user": {
            "_id": None,
            "username": None,
            "role": None,
            "ts": None,
            "botmaster": None,
            "badges": [],
            "xp": None,
            "gamesplayed": None,
            "gameswon": None,
            "gametime": None,
            "country": None,
            "supporter": None,
            "supporter_tier": 0,
            "verified": False,
            "badstanding": False,
            "league": {
                "gamesplayed": None,
                "gameswon": None,
                "rating": None,
                "glicko": None,
                "rd": None,
                "rank": None,
                "apm": None,
                "pps": None,
                "vs": None,
                "decaying": True,
                "standing": None,
                "standing_local": None,
                "prev_rank": None,
                "prev_at": None,
                "next_rank": None,
                "next_at": None,
                "percentile": None,
                "percentile_rank": None,
            },
            "avatar_revision": None,
            "banner_revision": None,
            "bio": None,
            "friend_count": None,
        }
    },
    "cache": {
        "status": None,
        "cached_at": None,
        "cached_until": None,
    },
    "error": None,
}


class Request:
    @staticmethod
    async def get(url: str, headers: dict = None) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                return await response.json()


class Cache_Status(enum.Enum):
    HIT = "hit"
    MISS = "miss"
    AWAITED = "awaited"


@dataclasses.dataclass
class Cache:
    status: Cache_Status
    cached_at: datetime.datetime
    cache_until: datetime.datetime


class Role(enum.Enum):
    anonymous = "anon"
    user = "user"
    bot = "bot"
    moderator = "mod"
    adminstrator = "admin"

    def __str__(self):
        return self.name.title()


@dataclasses.dataclass
class Badge:
    id: str
    label: str
    ts: typing.Optional[datetime.datetime]


class Rank(enum.Enum):
    unranked = "z"
    d = "d"
    d_plus = "d+"
    c_minus = "c-"
    c = "c"
    c_plus = "c+"
    b_minus = "b-"
    b = "b"
    b_plus = "b+"
    a_minus = "a-"
    a = "a"
    a_plus = "a+"
    s_minus = "s-"
    s = "s"
    s_plus = "s+"
    ss = "ss"
    u = "u"
    x = "x"

    def __str__(self) -> typing.AnyStr:
        return self.value if self.name != "unranked" else "Unranked"


@dataclasses.dataclass
class League:
    gamesplayed: int
    gameswon: int
    rating: float
    glicko: float
    rd: float
    rank: Rank
    apm: float
    pps: float
    vs: float
    decaying: bool
    standing: int
    standing_local: int
    prev_rank: typing.Optional[Rank]
    prev_at: typing.Optional[int]
    next_rank: typing.Optional[Rank]
    next_at: typing.Optional[int]
    percentile_rank: Rank
    percentile: float


@dataclasses.dataclass
class User:
    id: str
    username: str
    role: Role
    ts: typing.Optional[datetime.datetime]
    botmaster: typing.Optional[str]
    badges: typing.List[Badge]
    xp: float
    gamesplayed: int
    gameswon: int
    gametime: datetime.timedelta
    country: typing.Optional[str]
    badstanding: bool
    supporter: bool
    supporter_tier: int
    verified: bool
    league: typing.Optional[League]
    avatar_revision: typing.Optional[yarl.URL]
    banner_revision: typing.Optional[yarl.URL]
    bio: typing.Optional[str]
    friend_count: int


@dataclasses.dataclass
class Data:
    user: typing.Optional[User]


@dataclasses.dataclass
class PlayerAPI:
    success: bool
    error: typing.Optional[str]
    cache: typing.Optional[Cache]
    data: typing.Optional[Data]

    @classmethod
    async def get_player(cls,username: str) -> "PlayerAPI":
        await connect()
        cache = await db.fetch("SELECT * FROM cache WHERE username = $1", username)
        base_url = yarl.URL("https://ch.tetr.io/api/users")
        result = None
        if cache:

            result: dict = cache[0].data
            if not result["success"]:
                response = await Request.get(base_url / username)
                if not response["success"]:
                    raise APIError(result["error"])
                await db.execute(
                    "DELETE FROM cache_player_info WHERE username = $1", username
                )
                await db.execute(
                    "INSERT INTO cache_player_info(username, data) VALUES($1, $2)",
                    username,
                    orjson.dumps(response),
                )
                result = response

        copied = copy.deepcopy(complete)
        copied.update(result)  # replace the default values with the ones from the API
        args = copied
        args["cache"]["cached_at"] = datetime.datetime.fromtimestamp(
            args["cache"]["cached_at"] / 1000
        )
        args["cache"]["cached_until"] = datetime.datetime.fromtimestamp(
            args["cache"]["cached_until"] / 1000
        )
        args["user"]["badges"] = [Badge(**badge) for badge in args["user"]["badges"]]
        args["user"]["ts"] = timestring_to_datetime(args["user"]["ts"])
        args["league"]["prev_rank"] = (
            Rank(args["league"]["prev_rank"]) if args["league"]["prev_rank"] else None
        )
        args["league"]["rank"] = Rank(args["league"]["rank"])
        args["league"]["next_rank"] = (
            Rank(args["league"]["next_rank"]) if args["league"]["next_rank"] else None
        )
        args["league"]["percentile_rank"] = Rank(args["league"]["percentile_rank"])
        args["league"] = League(**args["league"])
        args["user"]["avatar_revision"] = yarl.URL(f'https://tetr.io/user-content/avatars/{args["user"]["_id"]}.jpg?rv={args["user"]["avatar_revision"]}') if args["user"]["avatar_revision"] else None
        args["user"]["banner_revision"] = yarl.URL(f'https://tetr.io/user-content/banners/{args["user"]["_id"]}.jpg?rv={args["user"]["banner_revision"]}') if args["user"]["banner_revision"] else None
        return cls(**args)


def timestring_to_datetime(time_string) -> datetime:
    return dateutil.parser.parse(time_string)
