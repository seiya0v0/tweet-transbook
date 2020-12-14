import server
import os

if __name__ == "__main__":
    if os.path.exists("./data"):
        os.mkdir("./data")
    server.run()