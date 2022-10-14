import sys
sys.path.append("..") # for cd in tests folder
sys.path.append(".") # for test outside tests folder
import typing
import src.utils.calc_stats as stats
from decimal import Decimal, ROUND_05UP
data_set: dict[str, typing.Union[int,float]] = {
    "apm": 42.94,
    "pps":1.5,
    "vs": 91,
    "rd": 60.89
}

# round those numbers 🥰

def test_app():
    assert float(Decimal(stats.app(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 0.4771
    
def test_ds_second():
    assert float(Decimal(stats.ds_second(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 0.1943
    
def test_ds_piece():
    assert float(Decimal(stats.ds_piece(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 0.1296

def test_app_ds_piece():
    assert float(Decimal(stats.app_ds_piece(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 0.6066

def test_cheese_index():
    assert float(Decimal(stats.cheese_index(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 40.7562 # pretty near 40.7475
    
def test_garbage_efficiency():
    assert float(Decimal(stats.garbage_efficiency(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 0.1236

def test_area():
    assert float(Decimal(stats.area(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 370.3596 # pretty near 370.319

def test_weighted_app():
    assert float(Decimal(stats.weighted_app(**data_set)).quantize(Decimal(".0001"),rounding=ROUND_05UP)) == 0.5084