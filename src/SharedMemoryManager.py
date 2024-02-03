import os
import struct
import errno
import subprocess


class SharedMemoryManager:
    def __init__(self, max_players=10, pipe_name='/tmp/shared_memory_pipe'):
        self.player_size = 12  # 4 bytes for int ID, 4 bytes each for two floats
        self.buffer_size = max_players * self.player_size
        self.player_data = {}
        self.pipe_name = pipe_name

        # Create the named pipe
        try:
            os.mkfifo(self.pipe_name)
        except FileExistsError:
            pass  # If the pipe already exists, no need to create it again

    def update_player(self, id, x, y):
        self.player_data[id] = (x, y)
        #self.write_to_shared_memory()

    def write_to_shared_memory(self):
        if( len(self.player_data) == 0):
            return
        serialized_data = b''
        for pid, (px, py) in self.player_data.items():
            serialized_data += struct.pack('iff', pid, px, py)

        self.write_to_pipe_non_blocking(self.pipe_name, serialized_data)

        # # Write to named pipe
        # with open(self.pipe_name, 'wb', buffering=0) as pipe:
        #     pipe.write(serialized_data)

    def write_to_pipe_non_blocking(self, pipe_name, data):
        mode = os.O_WRONLY | os.O_NONBLOCK
        try:
            pipe_fd = os.open(pipe_name, mode)
        except OSError as e:
            if e.errno == errno.ENOENT:
                print(f"Named pipe {pipe_name} does not exist.")
            elif e.errno == errno.EWOULDBLOCK:
                print(f"Write operation on {pipe_name} would block.")
            else:
                print(f"Opening named pipe failed: {e}")
                if self.ask_for_permission_tocreatepipe() == True:
                    self.write_to_pipe_non_blocking(self, pipe_name, data)
            return

        try:
            bytes_written = os.write(pipe_fd, data)
            print(f"Wrote {bytes_written} bytes to the pipe.")
        except OSError as e:
            if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                print("Writing to pipe would block, try again later.")
            else:
                print(f"Writing to pipe failed: {e}")
        finally:
            os.close(pipe_fd)

    def create_named_pipe(self,pipe_path):
        try:
            os.mkfifo(pipe_path)
            print(f"Named pipe created at: {pipe_path}")
        except FileExistsError:
            print(f"Named pipe already exists at: {pipe_path}")
        except Exception as e:
            print(f"Error creating named pipe: {e}")

    def ask_for_permission_tocreatepipe(self):
        user_input = input("Do you want to create the pipe? (y/n): ").strip().lower()
        if user_input == "y":
            #pipe_path = input("Enter the path for the named pipe: ").strip()
            self.create_named_pipe(self.pipe_name)
            return True
        else:
            print("No action taken.")     
            return False       

# # Example usage
# if __name__ == "__main__":
#     shm_manager = SharedMemoryManager(max_players=10)
#     shm_manager.update_player(1, 2.5, 3.5)
#     # ... More updates
