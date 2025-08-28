# shared_core/di/errors.py

class DependencyNotFound(Exception):
    """Raised when a requested dependency is not registered in the container."""
    def __init__(self, dependency):
        super().__init__(f"No provider registered for dependency: {dependency!r}")
        self.dependency = dependency
