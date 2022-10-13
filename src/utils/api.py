import dataclasses
import datetime
import enum
import typing

import aiohttp
import dateutil.parser
import yarl
from .db import db
from .errors import APIError
class Request:
    @staticmethod
    async def get(url: str, headers: dict = None):
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
@dataclasses.dataclass
class User:
    id: str
    username: str
    role: Role
    ts: typing.Optional[datetime.datetime]
    botmaster: typing.Optional["User"]
    badges: typing.List[Badge]
    xp: float
    gamesplayed: int
    gameswon: int
    gametime: datetime.timedelta
    country: typing.Optional[str]
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
    async def get_player(username:str) -> "PlayerAPI":
        cache = await db.fetch("SELECT * FROM cache WHERE username = $1", username)
        base_url = yarl.URL("https://ch.tetr.io/api/users")
        if cache:
            # filter some data that isn't exists or none
            result:dict = cache[0]
            if not result["success"]:
                response = await (await Request.get(base_url/username)).json()
                raise APIError(result["error"])
            
    
    
def timestring_to_datetime(time_string) -> datetime:
    return dateutil.parser.parse(time_string)
