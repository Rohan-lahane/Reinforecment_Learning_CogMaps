

import numpy as np
import matplotlib.pyplot  as plt
from mpl_toolkits.mplot3d import Axes3D
# from mpl_toolkits.mpl_toolkits.mplot3d import Axes3D
from actor import Actor

from pathlib import Path
from parameters import *

class Figure : 

  figure = None 

  def show(self):
    self.figure.show()
                        
  def close(self):
      plt.close(fig =self.figure)

      #can we compress this further 

class TrialFigure(Figure):

    watermaze = None
    rat = None
    log =None

    rat_positions_axis = None
    pref_directions_axis =None 
    value_estimate_axis = None

    def __init__(self,watermaze,rat,log):
        self.watermaze = watermaze
        self.rat =rat
        self.log = log

        self.create_figure_and_axis()
        self.configure_subplots()
        self.draw_subplots()

    def create_figure_and_axis(self):
        self.figure = plt.figure(figsize = (15, 5))
        grid = plt.GridSpec(1, 3, wspace = 0, hspace = 0)

        self.rat_positions_axis = self.figure.add_subplot(grid[0, 0])
        self.pref_directions_axis = self.figure.add_subplot(grid[0, 1])
        self.value_estimate_axis = self.figure.add_subplot(grid[0, 2], projection = "3d")

    def draw_watermaze(self, axis):
        center = (self.watermaze.center[0], self.watermaze.center[1])
        radius = self.watermaze.radius

        background = plt.Circle(center, radius, color = "#10AECC", zorder = 0)
        border = plt.Circle(center, radius, color = "#CC3C47", linewidth = 2, fill = False, zorder = 1)

        axis.add_artist(background)
        axis.add_artist(border)


    def draw_platform(self, axis):
        center = (self.watermaze.platform.center[0], self.watermaze.platform.center[1])
        radius = self.watermaze.platform.radius

        background = plt.Circle(center, radius,  color = "#E0C62A", zorder = 10)
        border = plt.Circle(center, radius, color = "#22A25C", linewidth = 1, fill = False, zorder = 11)

        axis.add_artist(background)
        axis.add_artist(border)


      
    def draw_rat_positions(self, axis):
        positions_x = [pos[0] for pos in self.log["position"]]
        positions_y = [pos[1] for pos in self.log["position"]]

        axis.scatter(positions_x, positions_y, c = np.arange(len(positions_x)),
                    cmap = "autumn", marker = ".", zorder = 20)
        axis.plot(positions_x, positions_y, color = "#193558", zorder = 21)



    def draw_preferred_directions(self, axis):
        positions_x = self.rat.place_cells.position_in_maze[:, 0] #placecells instead of rat ?
        positions_y = self.rat.place_cells.position_in_maze[:, 1]

        probabilities = self.log["action_probability"]
        preferred_directions_indices = np.argmax(probabilities.T, axis = 1)
        preferred_directions = [self.rat.actor.actions[i] for i in preferred_directions_indices]

        arrows_x = np.array([self.rat.pos_diff_by_direction[direction][0] for direction in preferred_directions])
        arrows_y = np.array([self.rat.pos_diff_by_direction[direction][1] for direction in preferred_directions])

        arrow_scale = probabilities[preferred_directions_indices][0]
        arrows_x *= arrow_scale
        arrows_y *= arrow_scale

        indices_to_keep = np.arange(0, len(positions_x), 21)
        axis.quiver(positions_x[indices_to_keep], positions_y[indices_to_keep],
                    arrows_x[indices_to_keep], arrows_y[indices_to_keep])  

    def draw_critic_values(self, axis):
        positions_x = self.rat.place_cells.position_in_maze[:, 0]
        positions_y = self.rat.place_cells.position_in_maze[:, 1]
        values = self.log["critic_vals"]

        axis.plot_trisurf(positions_x, positions_y, np.absolute(values),
                          linewidth = 0.2, edgecolor = "black", cmap = "RdBu")


    def configure_subplots(self):
        # X and Y limits for plots displaying the watermaze
        watermaze_xlims = [XO - (R_WATERMAZE * 1.1), XO + (R_WATERMAZE * 1.1)]
        watermaze_ylims = [YO - (R_WATERMAZE * 1.1), YO + (R_WATERMAZE * 1.1)]

        self.rat_positions_axis.set_title("Rat positions", fontsize = 12)
        self.rat_positions_axis.set_xlim(*watermaze_xlims)
        self.rat_positions_axis.set_ylim(*watermaze_ylims)
        self.rat_positions_axis.set_axis_off()
        self.rat_positions_axis.set_aspect("equal")

      
        self.pref_directions_axis.set_title("Preferred directions", fontsize = 12)
        self.pref_directions_axis.set_xlim(*watermaze_xlims)
        self.pref_directions_axis.set_ylim(*watermaze_ylims)
        self.pref_directions_axis.set_axis_off()
        self.pref_directions_axis.set_aspect("equal")

        self.value_estimate_axis.set_title("Value function estimate", fontsize = 12, pad = 20)
        self.value_estimate_axis.set_zlim(0, 1.3)
        self.value_estimate_axis.set_xticks([XO - R_WATERMAZE, XO, XO + R_WATERMAZE])
        self.value_estimate_axis.set_yticks([YO - R_WATERMAZE, YO, YO + R_WATERMAZE])
        #self.value_estimate_axis.set_aspect("equal")
        self.value_estimate_axis.set_aspect("auto")

    def draw_subplots(self):
        # rat positions
        self.draw_watermaze(self.rat_positions_axis)
        self.draw_platform(self.rat_positions_axis)
        self.draw_rat_positions(self.rat_positions_axis)

        # directions
        self.draw_watermaze(self.pref_directions_axis)
        self.draw_preferred_directions(self.pref_directions_axis)
        self.draw_platform(self.pref_directions_axis)

        # value function estimate
        self.draw_critic_values(self.value_estimate_axis)   


class RatPerformanceFigure(Figure):
  
  path_lengths = None
  path_lengths_std = None

  axis = None

  def __init__(self,logs_of_all_runs):
    self.compute_and_set_path_lengths(logs_of_all_runs)

    self.create_figure_and_axis()
    self.configure()
    self.draw()

 

  def compute_and_set_path_lengths(self, logs_of_all_runs):
      # For each run, count the average number of logs in each trial
      # (i.e. the number of rat moves, which have a fixed length)
      nb_logs = np.array([[len(logs["position"]) for logs in logs_of_one_run]
                         for logs_of_one_run in logs_of_all_runs])

      self.path_lengths = np.mean(nb_logs, axis = 0) * STEP_TIME * SPEED
      self.path_lengths_std = np.std(nb_logs * STEP_TIME * SPEED, axis = 0)


  def create_figure_and_axis(self):
        self.figure, self.axis = plt.subplots(figsize = (15, 9))


  def configure(self):
        # Set various axis parameters
        self.axis.set_title("Performance of the rat", fontsize = 22, pad = 10)
        self.axis.set_xlabel("Trials", fontsize = 16, labelpad = 20)
        self.axis.set_ylabel("Path length (meter)", fontsize = 16, labelpad = 10)
        self.axis.set_ylim(0, TRIAL_TIME * SPEED * 1.5)
        self.axis.tick_params(length = 0, labelsize = 12)

        # Add an horizontal grid to the plot
        self.axis.yaxis.grid()

        # Group the labels by day using X labels
        self.axis.xaxis.set_major_locator(plt.FixedLocator([2.5 + (i * 4) for i in range(0, 10)]))
        self.axis.xaxis.set_major_formatter(plt.FixedFormatter(["Day " + str(i) for i in range(1, 10)]))


  def draw(self):
        for day_index in range(9):
            # Compute some parametrs depending on the day index
            # trial_indices = None
            # trial_indices.np.arange((day_index * 4), (day_index * 4) + 4)
            trial_indices = np.arange((day_index * 4), (day_index * 4) + 4)
            marker_color = "#002340" if day_index % 2 == 0 else "#0068BF"
            background_color = "#75A1CE" if day_index % 2 == 0 else "#E9EFF5"

            # Add a background color to the plots of the day
            self.axis.axvspan(0.5 + day_index * 4, 0.5 + (day_index + 1) * 4,
                              facecolor = background_color)

            #print trial_indices 

            #Plot the path lengths (as connected dots)
            self.axis.errorbar(trial_indices + 1, self.path_lengths[trial_indices],
                               yerr = self.path_lengths_std[trial_indices],
                               color = marker_color, marker = "o", capsize = 5)

            # self.axis.errorbar(trial_indices + 1,self.compute_and_set_path_lengths(self,logs_of_all_runs),
            #                         yerr = self.compute_and_set_path_lengths(self,logs_of_all_runs),
            #                         color = marker_color, marker = "o", capsize = 5)