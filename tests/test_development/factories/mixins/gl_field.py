import factory


class GitlabFieldMixin(factory.django.DjangoModelFactory):
    gl_id = factory.Sequence(lambda seq: seq)
    gl_url = factory.Sequence(
        lambda seq: 'https://team-projector-{0}.com'.format(seq),
    )
