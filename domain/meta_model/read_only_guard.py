from domain.meta_model.probability_output import ProbabilityOutput


class ReadOnlyGuard:
    """
    Prevents probability output from being used as actions.
    """

    @staticmethod
    def assert_read_only(output: ProbabilityOutput) -> None:
        if not isinstance(output, ProbabilityOutput):
            raise TypeError("Invalid meta-model output type")
