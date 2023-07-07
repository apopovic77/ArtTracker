import numpy as np
from hmmlearn import hmm
import cv2

class RadialHMM:
    def __init__(self, threshold=0.7, n_areas=5, origin=(0.5, 0.5), center_radius=0.2, start_angle=0):
        self.n_areas = n_areas
        self.n_states = n_areas + 3  # Including outside entrance, outside exit, and center area

        self.start_angle = start_angle

        # Initialize the HMM
        self.model = hmm.GaussianHMM(n_components=self.n_states, covariance_type="full")

        # Set the start probabilities
        self.model.startprob_ = self.create_start_probabilities()

        # Create the transition matrix
        self.model.transmat_ = self.create_transition_matrix()

        trans_mat = self.read_transition_matrix_from_file('transition_matrix.txt')
        self.model.transmat_ = trans_mat

        # Parameters of the emission probabilities for each state
        self.model.means_ = np.zeros((self.n_states, 2))
        self.model.covars_ = np.tile(np.eye(2) * 0.01, (self.n_states, 1, 1))

        # Observations
        self.observations = []

        # Threshold for state change
        self.threshold = threshold

        # The last predicted state
        self.last_state = None

        # Origin and center radius
        self.origin = origin
        self.center_radius = center_radius

    def read_transition_matrix_from_file(self, filename):
        trans_probs = []
        with open(filename, 'r') as file:
            content = file.read()  # Read the whole file
            lines = content.split('\n')  # Split by carriage return
            n_components = len(lines) - 1  # Deduct 1 for the header line
            for line in lines[1:]:  # Skip the header
                if line:  # Only process non-empty lines
                    values = line.split()  # Split each line with spaces
                    trans_probs.append([float(v) for v in values[:n_components]])
        return np.array(trans_probs) 

    def create_start_probabilities(self):
        start_probs = np.full((self.n_states,), 1.0 / self.n_states)
        return start_probs

    def create_transition_matrix(self):
        transmat = np.zeros((self.n_states, self.n_states))

        # Distribute the transitions from the outside entrance equally across all sectors
        transmat[0, 1:self.n_areas+1] = 1.0 / self.n_areas

        # Distribute the transitions from all sectors to the outside exit equally
        transmat[1:self.n_areas+1, self.n_areas+1] = 1.0 / self.n_areas

        # Set the transitions within the areas
        for i in range(1, self.n_areas+1):
            for j in range(1, self.n_areas+1):
                if i != j:
                    transmat[i, j] = 1.0 / (self.n_areas - 1)

        # Set the transitions from the areas to the center area
        center_area_prob = 1.0 / (self.n_areas + 1)  # Equal probability for all areas
        transmat[1:self.n_areas+1, self.n_states - 1] = center_area_prob

        # Set the transitions from the center area to other areas
        transmat[self.n_states - 1, 1:self.n_areas+1] = 1.0 / self.n_areas  # Equal probability to all areas

        # Normalize the rows to sum to 1
        transmat /= np.sum(transmat, axis=1, keepdims=True)

        return transmat

    def update(self, x, y):
        # Convert x, y to polar coordinates
        dx = x - self.origin[0]
        dy = y - self.origin[1]
        angle = np.arctan2(dy, dx)

        # Calculate the distance from the origin
        distance = np.sqrt(dx ** 2 + dy ** 2)

        # Append new observation
        self.observations.append([angle, distance])

        # Predict the sequence of states for the observations
        observations_array = np.array(self.observations)
        if len(self.observations) >= 200:
            states = self.model.predict(observations_array[-200:])
        else:
            states = self.model.predict(observations_array)

        # Compute the state probabilities for each observation
        state_probs = self.model.predict_proba(observations_array)

        # If the last state is different from the current one and the probability is above the threshold, print a message
        if self.last_state is not None and self.last_state != states[-1] and state_probs[-1, states[-1]] > self.threshold:
            print(f"Person entered Area {states[-1]}")

        # Update the last state
        self.last_state = states[-1]
        

    def draw_areas(self, img_size=500, entrance_angle=0, exit_angle=np.pi):
        # Create a blank image
        img = np.ones((img_size, img_size, 3), dtype=np.uint8) * 255

        # Determine the center of the image
        center = (img_size // 2, img_size // 2)

        # Draw the center area
        cv2.circle(img, center, int(self.center_radius * img_size), (0, 255, 0), thickness=2)

        # Draw the outside entrance and exit lines
        entrance_point = (int(center[0] + np.cos(entrance_angle) * img_size / 2), 
                        int(center[1] + np.sin(entrance_angle) * img_size / 2))
        exit_point = (int(center[0] + np.cos(exit_angle) * img_size / 2), 
                    int(center[1] + np.sin(exit_angle) * img_size / 2))
        cv2.line(img, center, entrance_point, (0, 0, 255), thickness=2)
        cv2.line(img, center, exit_point, (255, 0, 0), thickness=2)

        # Draw the pie slices for the areas
        sector_angle = 2 * np.pi / self.n_areas
        for i in range(self.n_areas):
            start_point = (int(center[0] + np.cos(self.start_angle + i * sector_angle) * img_size / 2), 
                        int(center[1] + np.sin(self.start_angle + i * sector_angle) * img_size / 2))
            end_point = (int(center[0] + np.cos(self.start_angle + (i + 1) * sector_angle) * img_size / 2), 
                        int(center[1] + np.sin(self.start_angle + (i + 1) * sector_angle) * img_size / 2))
            cv2.line(img, center, start_point, (0, 0, 0), thickness=2)
            cv2.line(img, center, end_point, (0, 0, 0), thickness=2)

        cv2.imshow("Areas", img)


    def print_transition_matrix(self):
        # Get the transition matrix
        transmat = self.model.transmat_

        # Print the transition matrix
        print("Transition Matrix:")
        for row in transmat:
            print(["{:.2f}".format(x) for x in row])