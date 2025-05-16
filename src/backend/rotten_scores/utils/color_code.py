from typing import NamedTuple

GREEN = "#28a745"
YELLOW = "#ffc107"
RED = "#dc3545"
NO_SCORE = "#6c757d"


class ColorCode(NamedTuple):
    """
    A class to represent a color code.
    """
    color: str
    message: str


def get_color_by_score(score: int | float) -> ColorCode:
    """
    Returns a color code based on the score.
    :param score: The score to evaluate.
    :return: A string representing the color code.
    """
    if score is None or score == '':
        return ColorCode(NO_SCORE, "No score available")
    if isinstance(score, float):
        return _get_color_by_user_score(score)
    elif isinstance(score, int):
        return _get_color_by_critic_score(score)
    raise ValueError(f"Score must be an integer for critic score or a float for user score. Got {type(score)}.")


def _get_color_by_user_score(score: float) -> ColorCode:
    if not (0 <= score <= 10):
        raise ValueError("User score must be between 0 and 10.")

    if score >= 9:
        return ColorCode(GREEN, "Universal acclaim")
    if score >= 8:
        return ColorCode(GREEN, "Generally favorable")
    elif score >= 5:
        return ColorCode(YELLOW, "Mixed or average")
    elif score >= 3:
        return ColorCode(RED, "Generally unfavorable")
    return ColorCode(RED, "Overwhelming dislike")


def _get_color_by_critic_score(score: int) -> ColorCode:
    if not (0 <= score <= 100):
        raise ValueError("Critic score must be between 0 and 100.")
    mapped_score = score / 10
    return _get_color_by_user_score(mapped_score)
