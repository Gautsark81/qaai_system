class TrainingQueue:
    """
    Abstract queue for offline training jobs.
    """

    def enqueue(self, job):
        raise NotImplementedError
