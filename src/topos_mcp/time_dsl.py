"""
Time-based DSL implementation using Lark for parsing temporal expressions and commitments.
"""
from lark import Lark, Transformer, v_args
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Grammar for time expressions and commitments
TIME_GRAMMAR = """
    TIME.2: /([0-1]?[0-9]|2[0-3]):[0-5][0-9]/
    DATE.2: /\d{4}[\-\.\/]\d{2}[\-\.\/]\d{2}/
    
    ?start: commitment | time_statement

    commitment: "by" time_expr "i will" task  -> make_commitment
             | time_expr "i will" task        -> make_commitment
    task: WORD+                               -> join_words

    time_statement: time_expr                 -> time_only_expr

    ?time_expr: specific_time
             | relative_expr
             | named_time

    specific_time: DATE "at" TIME            -> datetime_at
                | DATE TIME?                 -> datetime
                | TIME                       -> time_only

    relative_expr: "in" duration             -> future_in
                | duration "from" "now"      -> future_from
                | "after" duration           -> future_after

    duration: NUMBER time_unit        -> make_duration
    
    !time_unit: "minute"  -> unit_minute
            | "minutes"  -> unit_minute
            | "hour"    -> unit_hour
            | "hours"   -> unit_hour
            | "day"     -> unit_day
            | "days"    -> unit_day
            | "week"    -> unit_week
            | "weeks"   -> unit_week
            | "month"   -> unit_month
            | "months"  -> unit_month

    named_time: "tomorrow"           -> tomorrow
              | "today"              -> today
              | "next" WEEKDAY       -> next_weekday
              | WEEKDAY              -> this_weekday

    WEEKDAY: "monday"
           | "tuesday"
           | "wednesday"
           | "thursday"
           | "friday"
           | "saturday"
           | "sunday"
    
    %import common.NUMBER
    %import common.WORD
    %import common.WS
    %ignore WS
"""

@v_args(inline=True)
class TimeTransformer(Transformer):
    """Transform parse tree into Python objects."""
    
    def __init__(self):
        super().__init__()
        self.now = datetime.now()
        self.weekdays = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }

    def make_commitment(self, time, task):
        return {
            'type': 'commitment',
            'time': time,
            'task': task
        }

    def join_words(self, *words):
        return ' '.join(str(word) for word in words)

    def datetime_at(self, date, time):
        return datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')

    def datetime(self, date, time=None):
        if time:
            return datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
        return datetime.strptime(str(date), '%Y-%m-%d')

    def time_only(self, time):
        time_obj = datetime.strptime(str(time), '%H:%M').time()
        return datetime.combine(self.now.date(), time_obj)

    def future_in(self, duration):
        return self.now + duration

    def future_from(self, duration):
        return self.now + duration

    def future_after(self, duration):
        return self.now + duration

    def make_duration(self, amount, unit):
        units_map = {
            'minute': timedelta(minutes=1),
            'minutes': timedelta(minutes=1),
            'hour': timedelta(hours=1),
            'hours': timedelta(hours=1),
            'day': timedelta(days=1),
            'days': timedelta(days=1),
            'week': timedelta(weeks=1),
            'weeks': timedelta(weeks=1),
            'month': timedelta(days=30),
            'months': timedelta(days=30)
        }
        return float(amount) * units_map[str(unit)]

    def unit_minute(self, _):
        return "minutes"
        
    def unit_hour(self, _):
        return "hours"
        
    def unit_day(self, _):
        return "days"
        
    def unit_week(self, _):
        return "weeks"
        
    def unit_month(self, _):
        return "months"

    def tomorrow(self):
        return self.now + timedelta(days=1)

    def today(self):
        return self.now

    def next_weekday(self, weekday):
        return self._get_next_weekday(str(weekday).lower(), next_week=True)

    def this_weekday(self, weekday):
        return self._get_next_weekday(str(weekday).lower())

    def _get_next_weekday(self, weekday: str, next_week: bool = False) -> datetime:
        target_day = self.weekdays[weekday]
        current_day = self.now.weekday()
        days_ahead = target_day - current_day
        if days_ahead <= 0 or next_week:
            days_ahead += 7
        return self.now + timedelta(days=days_ahead)

class TimeDSL:
    """Main interface for the time-based DSL."""
    
    def __init__(self):
        self.parser = Lark(TIME_GRAMMAR, parser='lalr', transformer=TimeTransformer())
        
    def parse(self, text: str) -> Dict[str, Any]:
        """Parse a time expression or commitment."""
        try:
            result = self.parser.parse(text.lower())
            
            # Handle Tree wrapping and format datetime for both commitment and time-only expressions
            if isinstance(result, dict) and result.get('time'):
                if hasattr(result['time'], 'children') and len(result['time'].children) > 0:
                    result['time'] = result['time'].children[0]
                if isinstance(result['time'], datetime):
                    result['time'] = result['time'].strftime('%Y-%m-%d %H:%M:%S')
            elif hasattr(result, 'children') and len(result.children) > 0:
                time_val = result.children[0]
                if isinstance(time_val, datetime):
                    result = {'time': time_val.strftime('%Y-%m-%d %H:%M:%S')}
                else:
                    result = {'time': time_val}
            
            return result
        except Exception as e:
            return {'error': str(e)}

    def time_only_expr(self, time_expr):
        """Handle non-commitment time expressions."""
        if hasattr(time_expr, 'children') and len(time_expr.children) > 0:
            time_expr = time_expr.children[0]
        if isinstance(time_expr, datetime):
            return {'time': time_expr.strftime('%Y-%m-%d %H:%M:%S')}
        return {'time': time_expr}

def example_usage():
    """Example usage of the TimeDSL."""
    dsl = TimeDSL()
    
    # Test various expressions
    examples = [
        # Specific times with 'by'
        "by 2024-01-24 14:30 i will complete the project",
        "by tomorrow i will send the report",
        "by next friday i will prepare the presentation",
        "by 15:00 i will attend the meeting",
        
        # Relative times with commitment
        "in 2 hours i will review the code",
        "3 days from now i will deploy the changes",
        
        # Time expressions without commitments
        "in 2 hours",
        "tomorrow",
        "next friday",
        "15:00",
        "3 days from now"
    ]
    
    print("Time DSL Examples:")
    print("-" * 50)
    for example in examples:
        result = dsl.parse(example)
        print(f"\nInput: {example}")
        print(f"Parsed: {result}")

if __name__ == "__main__":
    example_usage()
