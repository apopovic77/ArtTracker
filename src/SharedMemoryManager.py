import os
import struct

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

        # Write to named pipe
        with open(self.pipe_name, 'wb', buffering=0) as pipe:
            pipe.write(serialized_data)

# # Example usage
# if __name__ == "__main__":
#     shm_manager = SharedMemoryManager(max_players=10)
#     shm_manager.update_player(1, 2.5, 3.5)
#     # ... More updates
