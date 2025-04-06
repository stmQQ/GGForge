from app import create_app

app = create_app()  # 'prod' для продакшена

if __name__ == '__main__':
    with app.app_context():
        app.run()
