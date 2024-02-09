import os
import struct
import errno
import subprocess
import config


class SharedMemoryManager:
    def __init__(self, max_players=10, pipe_name=config.SHARED_MEM_PIPENAME):
        self.player_size = 12  # 4 bytes for int ID, 4 bytes each for two floats
        self.buffer_size = max_players * self.player_size
        self.player_data = {}
        self.pipe_name = pipe_name

        # Create the named pipe
        try:
            os.mkfifo(self.pipe_name)
        except FileExistsError:
            pass  # If the pipe already exists, no need to create it again

    def update_player(self, tracker_id, unique_id, x, y, mask, triangle):
        self.player_data[tracker_id] = (x, y, unique_id, mask, triangle)
        #self.write_to_shared_memory()

    # def write_to_shared_memory(self):
    #     if( len(self.player_data) == 0):
    #         return
    #     serialized_data = b''
    #     for pid, (px, py, unique_id) in self.player_data.items():
    #         serialized_data += struct.pack('iiff', pid, unique_id, px, py)

    #     self.write_to_pipe_non_blocking(self.pipe_name, serialized_data)
        
    #     # Write to named pipe
    #     #with open(self.pipe_name, 'wb', buffering=0) as pipe:
    #     #    pipe.write(serialized_data)

    #     self.player_data.clear()




    def write_to_shared_memory(self):
        # Check if there's data to write
        if not self.player_data:
            return
        
        serialized_data = b''
        
        # Serialize Player Data
        # First, write the number of players
        serialized_data += struct.pack('i', len(self.player_data))
        
        # Then, serialize each player's data
        for pid, (px, py, unique_id, mask, triangle) in self.player_data.items():
            serialized_data += struct.pack('iiff', pid, unique_id, px, py)

        serialized_data += struct.pack('i', len(self.player_data))
        
        # Then, serialize each mask
        for pid, (px, py, unique_id,mask, triangles) in self.player_data.items():

            # Number of points in the mask
            serialized_data += struct.pack('i', len(mask))
            # Points of the mask
            for x, y in mask:
                serialized_data += struct.pack('ff', x, y)

            # Serialize the number of triangles
            serialized_data += struct.pack('i', len(triangle))
            # Serialize triangle indices
            for triangle in triangles:
                for vertex_index in triangle:
                    serialized_data += struct.pack('i', vertex_index)

        # Now, serialized_data contains both the player data and the masks
        # Transfer the serialized data via your communication channel
        self.write_to_pipe_non_blocking(self.pipe_name, serialized_data)
        self.player_data.clear()

        


    def write_to_pipe_non_blocking(self, pipe_name, data):
        mode = os.O_WRONLY | os.O_NONBLOCK
        try:
            pipe_fd = os.open(pipe_name, mode)
        except OSError as e:
            if config.PRINT_DEBUG:
                if e.errno == errno.ENOENT:
                    print(f"Named pipe {pipe_name} does not exist.")
                elif e.errno == errno.EWOULDBLOCK:
                    print(f"Write operation on {pipe_name} would block.")
                else:
                    print(f"Opening named pipe failed: {e}")
            return

        try:
            bytes_written = os.write(pipe_fd, data)
            #print(f"Wrote {bytes_written} bytes to the pipe.")
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
