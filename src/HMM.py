from hmmlearn import hmm
import numpy as np
import cv2

class RealTimeHMM:
    def __init__(self, threshold=0.7):

        # Number of states
        self.n_states = 6

        # Initialize the HMM
        self.model = hmm.GaussianHMM(n_components=self.n_states, covariance_type="full")

        # Person always starts from the left (Area 1)
        self.model.startprob_ = np.array([1/6, 1/6, 1/6, 1/6, 1/6, 1/6])

        # Transition matrix (modify according to your specific case)
        self.model.transmat_ = np.array([
        [0.5, 0.5, 0.0, 0.0, 0.0, 0.0],
        [0.25, 0.5, 0.25, 0.0, 0.0, 0.0],
        [0.0, 0.25, 0.5, 0.25, 0.0, 0.0],
        [0.0, 0.0, 0.25, 0.5, 0.25, 0.0],
        [0.0, 0.0, 0.0, 0.25, 0.5, 0.25],
        [0.0, 0.0, 0.0, 0.0, 0.5, 0.5]
        ])

        # Parameters of the emission probabilities for each state
        self.model.means_ = np.array([[-0.1], [0.125], [0.375], [0.625], [0.875], [1.1]])
        self.model.covars_ = np.tile(np.array([[0.01]]), (self.n_states, 1, 1))


        # Observations
        self.observations = np.array([])

        # Threshold for state change
        self.threshold = threshold

        # The last predicted state
        self.last_state = None
    
    def print_transition_matrix(self):
        print("Transition Matrix:")
        n_states = self.model.n_components
        for i in range(n_states):
            row = " ".join(f"{self.model.transmat_[i, j]:.2f}" for j in range(n_states))
            print(row)

    def train(self):
        # Fit the model on the observations
        self.model.fit(self.observations.reshape(-1, 1))

    def update(self, new_observation):
        # Append new observation
        self.observations = np.append(self.observations, new_observation)

        # Predict the sequence of states for the observations
        if len(self.observations) >= 200:
            states = self.model.predict(self.observations[-200:].reshape(-1, 1))
        else:
            states = self.model.predict(self.observations.reshape(-1, 1))

        # Compute the state probabilities for each observation
        state_probs = self.model.predict_proba(self.observations.reshape(-1, 1))

        # If the last state is different from the current one and the probability is above the threshold, print a message
        if self.last_state is not None and self.last_state != states[-1] and state_probs[-1, states[-1]] > self.threshold:
            print(f"Person entered Area {states[-1]+1}")
            
        # Update the last state
        self.last_state = states[-1]

    def draw():
        last_observation = hmm.observations[-1]
        my_state = 0
        if(last_observation < 0):
            my_state = 0
        elif(last_observation < 0.25):
            my_state = 1            
        elif(last_observation < 0.5):
            my_state = 2
        elif(last_observation < 0.75):
            my_state = 3
        elif(last_observation < 1):
            my_state = 4
        else:
            my_state = 5
        draw_prediction_rectangle(debug_states, hmm.last_state,color=(0,255,0))    
        draw_prediction_rectangle(debug_states, my_state,color=(255,0,0), rectangle_height=50)    
        cv2.imshow("Empty Image", debug_states)
    
