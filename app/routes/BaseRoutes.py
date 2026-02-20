from app.blueprints import main
from app.controllers.BaseController import BaseController

@main.route('/', methods=['GET'])
def landing_page():
    return BaseController.landing_page()

@main.route('/explore', methods=['GET'])
def explore_page():
    return BaseController.explore_page()

@main.route('/component/<name>', methods=['GET'])
def get_component(name):
    return BaseController.get_component(name)