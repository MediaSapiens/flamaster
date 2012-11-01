from sqlalchemy import types


class ChoiceType(types.TypeDecorator):
    """Type which add additional functionality
    for choice_fields.
    Required sequence (tuple or list).
    Important: if you need to add a new value in choices,
    you must to add it at the end of sequence.
    """
    impl = types.Integer

    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super(ChoiceType, self).__init__(*args, **kwargs)

    def process_bind_param(self, value, dialect):
        return self.choices.index(value)

    def process_result_value(self, value, dialect):
        return self.choices[value]
