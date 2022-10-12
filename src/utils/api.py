import aiohttp
import typing
import enum
import datetime
import dataclasses
import dateutil.parser
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

@dataclasses.dataclass
class User:
    id: str
    username: str
    role: Role
    ts: typing.Optional[datetime.datetime]
    botmaster: typing.Optional["User"]
    badges: typing.List[Badge]
@dataclasses.dataclass
class Data:
    user: typing.Optional[User]
@dataclasses.dataclass
class PlayerAPI:
    success:bool
    error: typing.Optional[str]
    cache: typing.Optional[Cache]
    data: typing.Optional[Data]
    
def timestring_to_datetime(time_string) -> datetime:
    return dateutil.parser.parse(time_string)