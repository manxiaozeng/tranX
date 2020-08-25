from server.app import get_app
# Just here because floydhub needs an app.py in root
app = get_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=true)
