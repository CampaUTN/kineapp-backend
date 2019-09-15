class CanViewModelMixin:
    def can_view(self, user) -> bool:
        return self.can_edit_and_delete(user)
