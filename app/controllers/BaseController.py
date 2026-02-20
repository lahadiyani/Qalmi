from flask import render_template, url_for

class BaseController:
    @staticmethod
    def landing_page():
        return render_template('landing.html')
    
    @staticmethod
    def explore_page():
        return render_template('explore.html')
    
    @staticmethod
    def get_component(name):
        return render_template(f'components/{name}.html')
    

    
