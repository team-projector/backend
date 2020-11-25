import factory


class GitlabFieldMixin(factory.django.DjangoModelFactory):
    """Gitlab field mixin."""

    gl_id = factory.Sequence(lambda seq: seq + 1)
    gl_url = factory.Sequence(
        lambda seq: "https://team-projector-{0}.com".format(seq),
    )
