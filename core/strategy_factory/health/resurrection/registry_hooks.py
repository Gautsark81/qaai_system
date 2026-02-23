class ResurrectionRegistryMixin:
    def mark_resurrection_candidate(self, dna, state, reason, artifact):
        record = self.get(dna)
        record.state = state
        record.metadata["resurrection_reason"] = reason
        record.metadata["resurrection_artifact"] = artifact

    def record_resurrection_event(self, dna, event):
        self.events.append(event)
