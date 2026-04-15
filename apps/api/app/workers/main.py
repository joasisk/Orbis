import time

def main():
    while True:
        print("worker heartbeat")
        time.sleep(30)

if __name__ == "__main__":
    main()
