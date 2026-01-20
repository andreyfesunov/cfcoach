from datetime import datetime
from typing import Optional
from fastapi.templating import Jinja2Templates
from pathlib import Path


def get_template_engine() -> Jinja2Templates:
    template_dir = Path(__file__).parent / "templates"
    templates = Jinja2Templates(directory=str(template_dir))
    templates.env.globals["get_rating_color"] = get_rating_color
    templates.env.globals["get_problem_url"] = get_problem_url
    templates.env.globals["get_contest_url"] = get_contest_url
    templates.env.globals["format_rating"] = format_rating
    templates.env.globals["format_datetime"] = format_datetime
    return templates


def format_rating(rating: Optional[int]) -> str:
    if rating is None:
        return "N/A"
    return str(rating)


def format_datetime(dt: Optional[datetime]) -> str:
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_rating_color(rating: Optional[int]) -> str:
    if rating is None:
        return "gray"
    if rating < 1200:
        return "gray"
    elif rating < 1400:
        return "green"
    elif rating < 1600:
        return "cyan"
    elif rating < 1900:
        return "blue"
    elif rating < 2100:
        return "violet"
    elif rating < 2400:
        return "orange"
    else:
        return "red"


def get_problem_url(contest_id: Optional[int], problem_index: Optional[str]) -> str:
    if contest_id is None or problem_index is None:
        return "#"
    return f"https://codeforces.com/problemset/problem/{contest_id}/{problem_index}"


def get_contest_url(contest_id: Optional[int]) -> str:
    if contest_id is None:
        return "#"
    return f"https://codeforces.com/contest/{contest_id}"
