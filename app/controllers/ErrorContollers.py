from flask import render_template

class ErrorController:
    @staticmethod
    def not_found(error):
        return render_template('404.html'), 404
    
    @staticmethod
    def internal_error(error):
        return render_template('500.html'), 500