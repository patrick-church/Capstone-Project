# Capstone-Project

## StatSwing: An MLB Analytics Application

## Description

In today’s data-driven sports landscape, statistical insights have emerged as the primary means for both professional analysts and fans to deepen their understanding of player performance. Nowhere is this more true than in baseball, where nearly every action taken by hitters and fielders during a game is quantified and tracked by some metric.

The goal of this project repository is to develop an interactive interface that enables users to explore and compare baseball players' hitting statistics with a high level of detail and flexibility. The interface will utilize our in-depth dataset to allow users not only to compare players' core hitting metrics against each other, but also to dive into specific situational stats—such as performance against individual pitchers, at particular stadiums, or under unique game conditions. In addition to situational breakdowns, the platform will include options for observing a players' performance trend over time, giving users insight into how a player’s abilities have evolved across seasons, in different contexts, and during critical moments.

# Data Retrieval

Proposal Link: https://docs.google.com/document/d/1-FgHjzoIlp2tr4nq0ZzZZCuM64M7s6rnJ7g4rBsGdQI/edit?usp=sharing

## Getting Started

To run the current prototype application, navigate to the `statswing` project directory and run the command:

`python main.py`

## Files/Folders Included

`main.py`: File currently containing source code for the execution of the application; will eventually include a master function to allow for the project to be imported

`data`: Directory containing the raw player data pulled from FanGraphs

`src`: Directory containing the source code for the creation of the application interface and management of its interactive functions

`config.py`: File containing a series of dictionaries used by the GUI-related functions in `statswing_gui.py` and `statswing_utils.py`

`statswing_gui.py`: File containing all PyQt5 code relating to the StatSwing GUI, including loading/cleaning/filtering data, formatting components, and implementing interactivity

`statswing_utils.py`: File containing supplementary functions used in `statswing_gui.py`, some of which aren't used anymore but I left them in anyway because why not
