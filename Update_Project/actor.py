
import numpy as np
from numpy.linalg import norm         
from numpy.random import choice       
from tqdm import tqdm              

from parameters import * 
from basic_functions import random_position

from placells import *
from critic import Critic 

class Actor: 
  # ''' calculates probabilities of actions fronm place cell activations '''

  weights = None

  actions = [
     "top_left",
      "top",
      "top_right",
      "right",
      "bottom_right",
      "bottom",
      "bottom_left",
      "left"
  ]       

  def __init__(self):  
     self.reset_weights()

  def reset_weights(self):
    self.weights = np.zeros((len(self.actions),CELL_COUNT))

  def action_probability(self,place_cells):
      activations = np.dot(self.weights,place_cells.current_activation)

      max_activation = np.max(activations)
      softmax_activations = np.exp(2.0*(activations - max_activation))

      return softmax_activations/ softmax_activations.sum()

  def action_probability_in_maze(self, place_cells):
      activations = np.array([np.dot(self.weights,activation) for activation in place_cells.activation_in_maze ])

      max_activation = np.max(activations, axis = 1)
      softmax_activations = np.exp(2 * (activations.T - max_activation))
      return softmax_activations / softmax_activations.sum()

  def update_weights(self,place_cells, direction, error):

    direction_index = self.actions.index(direction)
    self.weights[direction_index,:] += A_LEARNING_RATE *(error*place_cells.prev_activation)