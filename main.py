import re
import socket
import threading
from config import *

PORT = 4269
IP = socket.gethostbyname(socket.gethostname())
ADDR = (IP, PORT)
FORMAT = 'utf-8'
SIZE = 1024


class Robot:
    def __init__(self):
        self.direction = UNINITIALIZED
        self.previous_coordinates = None
        self.turning = False
        self.obstacle_next_move = 0
        self.obstacle_move_around = [SERVER_TURN_RIGHT, SERVER_MOVE, SERVER_TURN_LEFT,
                                     SERVER_MOVE, SERVER_TURN_LEFT, SERVER_MOVE, SERVER_TURN_RIGHT]

    def get_direction(self, x, y, goal_X, goal_Y):
        if goal_Y > y:
            return UP
        if goal_Y < y:
            return DOWN
        if goal_X > x:
            return RIGHT
        if goal_X < x:
            return LEFT

    def move(self, x, y):
        if (self.turning or (x, y) != self.previous_coordinates):
            self.previous_coordinates = (x, y)
            new_direction = self.get_direction(x, y, 0, 0)
            if self.direction == new_direction:
                self.turning = False
                return SERVER_MOVE
            else:
                self.direction = (self.direction + 1) % 4
                self.turning = True
                return SERVER_TURN_RIGHT
        what_do = self.obstacle_move_around[self.obstacle_next_move]
        self.obstacle_next_move = (self.obstacle_next_move + 1) % 7
        if self.obstacle_next_move == 0: self.turning = True
        return what_do


def send_msg_to_robot(server_msg, connection):
    print(f"[SERVER_MSG] {server_msg}")
    server_msg = server_msg.encode(FORMAT)
    connection.send(server_msg)


def check_len(msg, stage):
    lenght = len(msg)
    if msg.endswith(b"\a"):
        lenght -= 1
    match stage[0]:
        case 0:
            match stage[1]:
                case 0:
                    return lenght <= CLIENT_USERNAME_LEN
                case 1:
                    return lenght <= CLIENT_KEY_ID_LEN
                case 2:
                    return lenght <= CLIENT_CONFIRMATION_LEN
                case _:  # Should not happen
                    return False
        case 1:
            match stage[1]:
                case 0:
                    return lenght <= CLIENT_MOVE_OPERATIONS
                case 1:
                    return lenght <= CLIENT_MESSAGE_LEN
        case _:  # Should not happen
            return False


def check_msg_format(msg, stage):
    match stage[0]:
        case 0:
            match stage[1]:
                case 1:
                    return msg.decode(FORMAT).isdecimal()
                case 2:
                    return msg.decode(FORMAT).isdecimal() # unnecessarily twice, don't ask pls
                case _:
                    return True
        case 1:
            match stage[1]:
                case 0:
                    if re.search("^OK {1}(-|[0-9])?( |[0-9])?( |[0-9])?( ){1}(-|[0-9])?([0-9])?([0-9])$", msg.decode(FORMAT)):
                        return True
                    return False
                case _:
                    return True
        case _:
            return True


def get_data(msg, connection, stage):
    tmp = msg
    while not tmp.endswith(b"\a\b"):
        if b"\a\b" not in tmp:
            if (not check_len(tmp, stage)):
                return "Well this robot is not working properly and his messages are too long\a\b"
        connection.settimeout(TIMEOUT)
        tmp += connection.recv(SIZE)
    messages = tmp.split(b"\a\b")
    return messages[:-1]


def name_into_hash(name):
    sum = 0
    # print(name)
    for word in name:
        sum += int(word)
        # print(int(word))
    # print(sum)
    return (sum * 1000) % 65536


def compare_hash(msg, hashed_name, key_id):
    hashed_name += CLIENT_KEY[key_id.decode(FORMAT)]
    m_hash = hashed_name % 65536
    return m_hash == int(msg)


def get_coordinates(msg):
    data = msg.split()
    return int(data[1]), int(data[2])


def handle_robot(connection, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    recharging = False
    getting_secret = False
    get_out = False
    obstacle = False
    stage = [0, 0]
    key_id = None
    robot = Robot()
    try:
        while True:
            if not recharging:
                connection.settimeout(TIMEOUT)
            else:
                connection.settimeout(TIMEOUT_RECHARGING)
            data = connection.recv(SIZE)
            if data:
                tmp_msgs = get_data(data, connection, stage)
                if "Well this robot is not working properly and his messages are too long\a\b" in tmp_msgs:
                    send_msg_to_robot(SERVER_SYNTAX_ERROR, connection)
                    get_out = True
                    break
                for msg in tmp_msgs:
                    print(f"[CLIENT_MSG] {msg}")

                    if CLIENT_RECHARGING in msg:
                        recharging = True
                        continue

                    if CLIENT_FULL_POWER in msg:
                        if not recharging:
                            send_msg_to_robot(SERVER_LOGIC_ERROR, connection)
                            get_out = True
                            break
                        recharging = False
                        continue

                    if recharging:
                        send_msg_to_robot(SERVER_LOGIC_ERROR, connection)
                        get_out = True
                        break

                    if (not check_len(msg, stage) or not check_msg_format(msg, stage)):
                        send_msg_to_robot(SERVER_SYNTAX_ERROR, connection)
                        get_out = True
                        break

                    if getting_secret:
                        print(f"[Secret] {msg}")
                        send_msg_to_robot(SERVER_LOGOUT, connection)
                        get_out = True
                        break

                    match stage[0]:
                        case 0:
                            match stage[1]:
                                case 0:
                                    my_hash = name_into_hash(msg)
                                    hashed_name = my_hash
                                    send_msg_to_robot(
                                        SERVER_KEY_REQUEST, connection)
                                    stage[1] += 1
                                case 1:
                                    if not int(msg) in [0, 1, 2, 3, 4]:
                                        send_msg_to_robot(
                                            SERVER_KEY_OUT_OF_RANGE_ERROR, connection)
                                        get_out = True
                                        break
                                    key_id = msg
                                    my_hash += SERVER_KEY[key_id.decode(
                                        FORMAT)]
                                    SERVER_CONFIRMATION = str(my_hash % 65536)
                                    send_msg_to_robot(
                                        SERVER_CONFIRMATION + "\a\b", connection)
                                    stage[1] += 1
                                case 2:
                                    if compare_hash(msg, hashed_name, key_id):
                                        send_msg_to_robot(
                                            SERVER_OK, connection)
                                        send_msg_to_robot(
                                            SERVER_MOVE, connection)
                                        stage[0] += 1
                                        stage[1] = 0
                                    else:
                                        send_msg_to_robot(
                                            SERVER_LOGIN_FAILED, connection)
                                        get_out = True
                                        break
                        case 1:
                            x, y = get_coordinates(msg)
                            if x == 0 and y == 0:
                                send_msg_to_robot(SERVER_PICK_UP, connection)
                                getting_secret = True
                                stage[1] = 1
                                break
                            if robot.direction == UNINITIALIZED:
                                if obstacle:
                                    send_msg_to_robot(
                                        SERVER_MOVE, connection)
                                    obstacle = False
                                    continue

                                if robot.previous_coordinates:
                                    if robot.previous_coordinates != (x, y):
                                        robot.direction = robot.get_direction(robot.previous_coordinates[0],
                                                                              robot.previous_coordinates[1], x, y)
                                        send_msg_to_robot(
                                            robot.move(x, y), connection)
                                        continue

                                    else:
                                        send_msg_to_robot(
                                            SERVER_TURN_RIGHT, connection)
                                        obstacle = True
                                        continue
                                
                                robot.previous_coordinates = (x, y)
                                send_msg_to_robot(
                                    SERVER_MOVE, connection)
                                continue

                            send_msg_to_robot(
                                robot.move(x, y), connection)

            if get_out:
                break

    except socket.timeout:
        print('What took you so long?')
    finally:
        connection.close()


def main():
    # Cause on the internet they said this is how you do it
    print(f"[LISTENING] Server is listening on {IP}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    while True:
        connection, addr = server.accept()
        connection.settimeout(TIMEOUT)
        thread = threading.Thread(target=handle_robot, args=(connection, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    main()
