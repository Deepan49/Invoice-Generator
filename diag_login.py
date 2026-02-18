from app import create_app

def diag():
    app = create_app()
    lm = app.login_manager
    print(f"LoginManager instance: {lm}")
    print(f"User callback: {lm.user_callback}")
    
if __name__ == '__main__':
    diag()
