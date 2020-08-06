# -*- coding: utf-8 -*-

import factory


class GlUserFactory(factory.DictFactory):
    """Gitlab user factory."""

    id = factory.Faker("random_int")  # noqa: WPS125, A003
    name = factory.Sequence(lambda seq: "User {0}".format(seq))
    public_email = factory.Sequence(
        lambda seq: "public{0}@mail.com".format(seq),
    )
    username = factory.Sequence(lambda seq: "user_name{0}".format(seq))
    state = "active"
    avatar_url = factory.Faker("url")
    web_url = factory.Faker("url")
