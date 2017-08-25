# Copyright 2017 Red Hat, Inc.
# License: GPLv3 or any later version

score_constants = None


def get_score_constants():
    global score_constants

    if score_constants is None:
        # Lazy-import this module to avoid circular deps
        from .. import models
        score_constants = models.MetricScoreConstants.objects.all()[:1].get()

    return score_constants


def green_score():
    return get_score_constants().green_score


def yellow_score():
    return get_score_constants().yellow_score


def red_score():
    return get_score_constants().red_score


def ry_boundary():
    return get_score_constants().ry_boundary


def yg_boundary():
    return get_score_constants().yg_boundary


def score_to_colour(score):
    """
    Return string containing colour based for score provided

    @arg score Health Score of project
    @returns "red", "green" or "yellow"
    """

    if score is None:
        return 'gray'

    if score > yg_boundary():
        return 'green'

    elif score > ry_boundary():
        return 'yellow'

    else:
        return 'red'


__all__ = [
    'green_score',
    'yellow_score',
    'red_score',
    'ry_boundary',
    'yg_boundary',
    'score_to_colour'
]
