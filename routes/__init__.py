def register_blueprints(app):
    from .image_generation import image_generation_bp
    app.register_blueprint(image_generation_bp)
