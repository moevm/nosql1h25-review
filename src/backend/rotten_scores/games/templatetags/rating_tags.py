from src.backend.rotten_scores.utils.color_code import get_color_by_score

from django import template

register = template.Library()


@register.filter
def get_color(score: int | float) -> str:
    """
    Returns a color code based on the score.
    :param score: The score to evaluate.
    :return: A string representing the color code.
    """
    return get_color_by_score(score).color


@register.filter
def get_message(score: int | float) -> str:
    """
    Returns a message based on the score.
    :param score: The score to evaluate.
    :return: A string representing the message.
    """
    return get_color_by_score(score).message
