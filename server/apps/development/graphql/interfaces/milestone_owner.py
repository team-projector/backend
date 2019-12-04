# -*- coding: utf-8 -*-

import graphene


class MilestoneOwner(graphene.Interface):
    """Milestone owner interface."""

    id = graphene.ID(required=True)  # noqa: A003
    title = graphene.String()
    full_title = graphene.String()
    gl_id = graphene.Int()
    gl_url = graphene.String()
    gl_last_sync = graphene.DateTime()
    gl_avatar = graphene.String()
