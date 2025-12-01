def tc(test_id):
    """Décorateur pour attribuer un ID de test à une fonction de test."""
    def decorator(func):
        func.test_case_id = test_id
        return func
    return decorator