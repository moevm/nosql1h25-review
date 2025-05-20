from src.utils.color_code import get_color_by_score

from django import template

register = template.Library()


@register.filter
def get_user_color(score: int | float) -> str:
    """
    Returns a color code based on the score.
    :param score: The score to evaluate.
    :return: A string representing the color code.
    """
    return get_color_by_score(score, "user").color


@register.filter
def get_critic_color(score: int | float) -> str:
    """
    Returns a color code based on the score.
    :param score: The score to evaluate.
    :return: A string representing the color code.
    """
    return get_color_by_score(score, "critic").color


@register.filter
def get_user_message(score: int | float) -> str:
    """
    Returns a message based on the score.
    :param score: The score to evaluate.
    :return: A string representing the message.
    """
    return get_color_by_score(score, "user").message


@register.filter
def get_critic_message(score: int | float) -> str:
    """
    Returns a message based on the score.
    :param score: The score to evaluate.
    :return: A string representing the message.
    """
    return get_color_by_score(score, "critic").message


@register.filter
def longer_than(value: str, arg: int):
    return len(value) > int(arg)
