import copy
import dataclasses
import datetime
import enum
import typing

import aiohttp
import dateutil.parser
import orjson
import yarl

from . import sqls
from .errors import APIError


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
    cached_until: datetime.datetime


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
    glicko: typing.Optional[float]
    rd: typing.Optional[float]
    rank: Rank
    apm: typing.Optional[float]
    pps: typing.Optional[float]
    vs: typing.Optional[float]
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
    _id: str
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
    async def get_player(cls, username: str) -> "PlayerAPI":
        db = sqls.EasySQL()
        await db.connect()
        cache = await db.fetch("SELECT * FROM cache WHERE username = $1", username)
        base_url = yarl.URL("https://ch.tetr.io/api/users")
        result = None
        if cache:
            print("cached response")
            print(cache)
            result: dict = orjson.loads(cache[username.lower()].encode("utf-8"))
            if not result["success"]:
                response = await Request.get(base_url / username)
                if not response["success"]:
                    raise APIError(result["error"])
                await db.execute(
                    "DELETE FROM cache WHERE username = $1", username.lower()
                )
                await db.execute(
                    "INSERT INTO cache(username, data) VALUES($1, $2)",
                    username.lower(),
                    orjson.dumps(response).decode("utf-8"),
                )
                result = response
        else:
            print("uncached response")
            result = await Request.get(base_url / username)
            await db.execute(
                "INSERT INTO cache(username, data) VALUES($1, $2)",
                username.lower(),
                orjson.dumps(result).decode("utf-8"),
            )

        args = result
        args["cache"]["cached_at"] = datetime.datetime.fromtimestamp(
            args["cache"]["cached_at"] / 1000
            if args["cache"]["cached_at"]
            else datetime.datetime.now().timestamp()
        )
        args["data"]["user"]["league"]["glicko"] = args["data"]["user"]["league"].get(
            "glicko", None
        )
        args["data"]["user"]["league"]["rd"] = args["data"]["user"]["league"].get(
            "rd", None
        )
        args["data"]["user"]["league"]["apm"] = args["data"]["user"]["league"].get(
            "apm", None
        )
        args["data"]["user"]["league"]["pps"] = args["data"]["user"]["league"].get(
            "pps", None
        )
        args["data"]["user"]["league"]["vs"] = args["data"]["user"]["league"].get(
            "vs", None
        )
        args["cache"]["cached_until"] = datetime.datetime.fromtimestamp(
            args["cache"]["cached_until"] / 1000
            if args["cache"]["cached_until"]
            else datetime.datetime.now().timestamp()
        )
        args["data"]["user"]["supporter"] = args["data"]["user"].get(
            "supporter", False
        )  # wow osk
        args["data"]["user"]["friend_count"] = args["data"]["user"].get(
            "friend_count", 0
        )  # wow osk
        args["data"]["user"]["bio"] = args["data"]["user"].get("bio", None)
        args["cache"]["status"] = Cache_Status(args["cache"]["status"])
        args["data"]["user"]["botmaster"] = (
            args["data"]["user"]["botmaster"]
            if args["data"]["user"].get("botmaster", None)
            else None
        )
        args["data"]["user"]["badstanding"] = (
            args["data"]["user"]["badstanding"]
            if args["data"]["user"].get("badstanding", None)
            else None
        )
        args["data"]["user"]["gametime"] = (
            datetime.timedelta(seconds=args["data"]["user"]["gametime"])
            if args["data"]["user"].get("gametime", None)
            else None
        )
        args["error"] = args["error"] if args.get("error", None) else None
        args["cache"] = Cache(**args["cache"])
        new_badge_info = []
        for badge in args["data"]["user"]["badges"]:
            if not badge.get("ts", None):
                badge["ts"] = None
            else:
                badge["ts"] = timestring_to_datetime(badge["ts"])
            new_badge_info.append(badge)
        args["data"]["user"]["badges"] = new_badge_info
        args["data"]["user"]["badges"] = [
            Badge(**badge) for badge in args["data"]["user"]["badges"]
        ]
        args["data"]["user"]["ts"] = (
            timestring_to_datetime(args["data"]["user"]["ts"])
            if args["data"]["user"].get("ts", None)
            else None
        )
        args["data"]["user"]["league"]["prev_rank"] = (
            Rank(args["data"]["user"]["league"]["prev_rank"])
            if args["data"]["user"]["league"]["prev_rank"]
            else None
        )
        args["data"]["user"]["league"]["rank"] = Rank(
            args["data"]["user"]["league"]["rank"]
        )
        args["data"]["user"]["league"]["next_rank"] = (
            Rank(args["data"]["user"]["league"]["next_rank"])
            if args["data"]["user"]["league"]["next_rank"]
            else None
        )
        args["data"]["user"]["league"]["percentile_rank"] = Rank(
            args["data"]["user"]["league"]["percentile_rank"]
        )
        args["data"]["user"]["league"] = League(**args["data"]["user"]["league"])
        args["data"]["user"]["avatar_revision"] = (
            yarl.URL(
                f'https://tetr.io/user-content/avatars/{args["data"]["user"]["_id"]}.jpg?rv={args["data"]["user"]["avatar_revision"]}'
            )
            if args["data"]["user"].get("avatar_revision", None)
            else None
        )
        args["data"]["user"]["banner_revision"] = (
            yarl.URL(
                f'https://tetr.io/user-content/banners/{args["data"]["user"]["_id"]}.jpg?rv={args["data"]["user"]["banner_revision"]}'
            )
            if args["data"]["user"].get("banner_revision", None)
            else None
        )

        args["data"]["user"] = User(**args["data"]["user"])
        args["data"] = Data(**args["data"])
        return cls(**args)


def timestring_to_datetime(time_string) -> datetime:
    return dateutil.parser.parse(time_string)
