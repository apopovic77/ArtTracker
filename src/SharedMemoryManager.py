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

    def update_player(self, tracker_id, unique_id, x, y):
        self.player_data[tracker_id] = (x, y, unique_id)
        #self.write_to_shared_memory()

    def write_to_shared_memory(self):
        if( len(self.player_data) == 0):
            return
        serialized_data = b''
        for pid, (px, py, unique_id) in self.player_data.items():
            serialized_data += struct.pack('iiff', pid, unique_id, px, py)

        #self.write_to_pipe_non_blocking(self.pipe_name, serialized_data)
        #self.testdeserialize(serialized_data)
        # # Write to named pipe
        with open(self.pipe_name, 'wb', buffering=0) as pipe:
            pipe.write(serialized_data)

        self.player_data.clear()
        


    def testdeserialize(self, serialized_data):
        # Calculate the size of each chunk (iiff = 4 bytes for int, 4 bytes for int, 4 bytes for float, 4 bytes for float)
        chunk_size = struct.calcsize('iiff')

        # Initialize an empty dictionary to hold deserialized player data
        deserialized_player_data = {}

        # Start index for slicing serialized_data
        start = 0

        # Loop until the entire serialized_data has been processed
        while start < len(serialized_data):
            # Extract a chunk of data
            chunk = serialized_data[start:start+chunk_size]
            
            # Deserialize the chunk
            pid, unique_id, px, py = struct.unpack('iiff', chunk)
            
            # Store the deserialized data using pid as the key
            deserialized_player_data[pid] = (px, py, unique_id)
            
            # Move the start index to the next chunk
            start += chunk_size

        # At this point, deserialized_player_data contains all the player data deserialized
        print(deserialized_player_data)        

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
