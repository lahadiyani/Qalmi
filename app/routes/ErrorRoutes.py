from app.blueprints import main
from app.controllers.ErrorContollers import ErrorController

@main.app_errorhandler(404)
def not_found(error):
    return ErrorController.not_found(error)

@main.app_errorhandler(500)
def internal_error(error):
    return ErrorController.internal_error(error)