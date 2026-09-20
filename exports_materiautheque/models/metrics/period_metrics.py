# -*- coding: utf-8 -*-
"""Metrics that don't read any model -- they just echo the export's own date range"""

from .base import register_metric


@register_metric('period.date_from')
def date_from(env, date_from=None, **kw):
    return date_from


@register_metric('period.date_to')
def date_to(env, date_to=None, **kw):
    return date_to
