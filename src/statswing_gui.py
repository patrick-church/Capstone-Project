import numpy as np
import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QHeaderView,
    QLabel, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QGridLayout, QSizePolicy
)
from src.config import TEAM_NAME_MAPPING, STAT_MAPPING, STAT_DESCRIPTIONS
from src.statswing_utils import get_dataset_column
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatSwingApp(QMainWindow):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.setWindowTitle("StatSwing Test")
        self.setGeometry(100, 100, 1000, 800)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.create_player_tab(), "Player Analytics")
        self.tabs.addTab(self.create_compare_tab(), "Compare Players")
        self.tabs.addTab(self.create_career_tab(), "Career Stats")

    def create_career_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        # Player selection dropdown
        self.career_player_dropdown = QComboBox()
        self.career_player_dropdown.addItems(self.data['Name'].unique())
        self.career_player_dropdown.currentTextChanged.connect(self.update_career_table)

        self.career_stats_table = QTableWidget()

        layout.addWidget(QLabel("Select Player:"))
        layout.addWidget(self.career_player_dropdown)
        layout.addWidget(self.career_stats_table)

        tab.setLayout(layout)
        return tab

    def update_career_table(self, player_name: str) -> None:


    # Filter the dataset for career stats (Season Year == 0)
        player_career_data = self.data[
            (self.data['Name'] == player_name) & (self.data['Season Year'] == 0)
        ]

        career_averages = self.data[self.data['Name'] == "Career Average"]

        if player_career_data.empty or career_averages.empty:
            self.career_stats_table.clear()
            self.career_stats_table.setRowCount(0)
            self.career_stats_table.setColumnCount(0)
            self.career_stats_table.setHorizontalHeaderLabels([])
            return

        player_stats = player_career_data.iloc[0]
        career_averages = career_averages.iloc[0]

        stats_columns = ["G", "PA", "HR", "R", "RBI", "SB", "BB%", "K%", "AVG", "OBP", "SLG", "wOBA"]

        stats_data = [
            (stat, player_stats[stat], career_averages[stat])
            for stat in stats_columns
        ]

        self.career_stats_table.clear()
        self.career_stats_table.setRowCount(len(stats_columns))
        self.career_stats_table.setColumnCount(3)  # Columns: Stat, Player Value, Career Avg
        self.career_stats_table.setHorizontalHeaderLabels(["Statistic", "Player Value", "Career Avg"])

        for row, (stat_name, player_value, league_value) in enumerate(stats_data):
            self.career_stats_table.setItem(row, 0, QTableWidgetItem(stat_name))  # Statistic
            self.career_stats_table.setItem(row, 1, QTableWidgetItem(f"{player_value:.2f}"))  # Player Value
            self.career_stats_table.setItem(row, 2, QTableWidgetItem(f"{league_value:.2f}"))  # Career Avg

        self.career_stats_table.resizeColumnsToContents()
        self.career_stats_table.resizeRowsToContents()
        self.career_stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.career_stats_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    def create_player_tab(self) -> QWidget:
        tab = QWidget()
        layout = QGridLayout()

        # Team selection dropdown
        self.team_dropdown = QComboBox()
        self.team_dropdown.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        team_names = ['All Teams'] + [TEAM_NAME_MAPPING.get(team, team) for team in sorted(self.data['Team'].unique())]
        self.team_dropdown.addItems(team_names)
        self.team_dropdown.currentTextChanged.connect(self.update_player_dropdown)

        # Player selection dropdown
        self.player_dropdown = QComboBox()
        self.player_dropdown.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.update_player_dropdown('All Teams')
        self.player_dropdown.currentTextChanged.connect(self.update_player_table)
        self.player_dropdown.currentTextChanged.connect(self.update_season_dropdowns)

        # Season selection dropdowns
        self.start_season_dropdown = QComboBox()
        self.start_season_dropdown.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.end_season_dropdown = QComboBox()
        self.end_season_dropdown.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.start_season_dropdown.currentTextChanged.connect(self.update_player_table)
        self.end_season_dropdown.currentTextChanged.connect(self.update_player_table)

        self.player_stats_table = QTableWidget()
        self.player_stats_table.itemDoubleClicked.connect(self.handle_double_click)
        #self.player_stats_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        #self.figure_player = Figure()
        #self.canvas_player = FigureCanvas(self.figure_player)
        #self.canvas_player.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.canvas_player.setParent(tab)  # Explicitly set the parent to ensure proper embedding

        # Add widgets to the grid layout
        layout.addWidget(QLabel('Select Team:'), 0, 0)
        layout.addWidget(self.team_dropdown, 0, 1)
        layout.addWidget(QLabel('Select Player:'), 0, 2)
        layout.addWidget(self.player_dropdown, 0, 3)
        layout.addWidget(QLabel('Start Season:'), 1, 0)
        layout.addWidget(self.start_season_dropdown, 1, 1)
        layout.addWidget(QLabel('End Season:'), 1, 2)
        layout.addWidget(self.end_season_dropdown, 1, 3)
        layout.addWidget(self.player_stats_table, 2, 0, 1, 4)
        #layout.addWidget(self.canvas_player, 3, 0, 1, 4)

        tab.setLayout(layout)
        return tab
    
    def handle_double_click(self, item: QTableWidgetItem) -> None:
        if item.column() == 0:
            stat_name = item.text()
            description = STAT_DESCRIPTIONS.get(stat_name, 'No description available')
            QMessageBox.information(self, f'About {stat_name}', description)
        elif item.column() == 1:
            stat_name = self.player_stats_table.item(item.row(), 0).text()
            self.compare_to_average(stat_name)

    def compare_to_average(self, stat_name: str) -> None:
        stat_col = get_dataset_column(stat_name)
        start_season = int(self.start_season_dropdown.currentText())
        end_season = int(self.end_season_dropdown.currentText())
        player_name = self.player_dropdown.currentText()
        filtered_data = self.data[(self.data['Season Year'] >= start_season) & (self.data['Season Year'] <= end_season)]

        grouped_data = (
            filtered_data.groupby('Name')[stat_col]
            .sum()
            .reset_index()
            .rename(columns = {stat_col: 'TotalStat'})
        )

        player_stat = grouped_data[grouped_data['Name'] == player_name]
        player_val = player_stat['TotalStat'].iloc[0]
        other_player_stats = grouped_data[grouped_data['Name'] != player_name]
        other_player_avg = other_player_stats['TotalStat'].mean()
        self.show_compare_chart(player_name, stat_name, player_val, other_player_avg, start_season, end_season)

    def show_compare_chart(self, player_name: str, stat_name: str, player_val: float, other_player_avg: float, start_season: int, end_season: int) -> None:
        fig = Figure(figsize = (6, 4))
        ax = fig.add_subplot(111)

        bars = ax.barh(
            ['Other Players (Avg)', player_name],
            [other_player_avg, player_val],
            color = ['blue', 'green' if player_val >= other_player_avg else 'red']
        )

        ax.set_title(f'Total {stat_name} Comparison ({start_season}-{end_season})')
        ax.set_ylabel(f'Total {stat_name}')
        ax.bar_label(bars, fmt = '%.2f')

        self.chart_window = QWidget()
        self.chart_window.setWindowTitle(f'Stat Comparison')

        canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(canvas)
        self.chart_window.setLayout(layout)
        self.chart_window.show()
    
    def update_player_dropdown(self, team_name: str) -> None:
        '''
        
        Updates the player dropdown menu based on the selected team
        
        '''
        if team_name == 'All Teams':
            filtered_data = self.data
        else:
            team_abbr = {v: k for k, v in TEAM_NAME_MAPPING.items()}.get(team_name, team_name)
            filtered_data = self.data[self.data['Team'] == team_abbr]
        self.player_dropdown.clear()
        self.player_dropdown.addItems(filtered_data['Name'].unique())

    def update_season_dropdowns(self) -> None:
       '''
       
       Updates the start and end season dropdown menus based on the selected player
       
       
       '''
       player_name = self.player_dropdown.currentText()
       if not player_name:
           self.start_season_dropdown.clear()
           self.end_season_dropdown.clear()
           return
       
       player_data = self.data[self.data['Name'] == player_name]
       if player_data.empty:
           self.start_season_dropdown.clear()
           self.end_season_dropdown.clear()
           return
       
       active_seasons = sorted(player_data['Season Year'].unique())
       active_seasons = np.delete(active_seasons, 0)
       self.start_season_dropdown.clear()
       self.end_season_dropdown.clear()
       self.start_season_dropdown.addItems(map(str, active_seasons))
       self.end_season_dropdown.addItems(map(str, active_seasons))

    def update_player_table(self) -> None:
        '''
        
        Updates the information displayed in the player table based on dropdown menu values
        
        '''
        player_name = self.player_dropdown.currentText()
        start_season = self.start_season_dropdown.currentText()
        end_season = self.end_season_dropdown.currentText()

        if not player_name or not start_season or not end_season:
            self.player_stats_table.clear()
            self.player_stats_table.setRowCount(0)
            self.player_stats_table.setColumnCount(0)
            self.player_stats_table.setHorizontalHeaderLabels([])
            return

        # Filter for player stats in the selected seasons
        filtered_player_data = self.data[
            (self.data['Name'] == player_name) &
            (self.data['Season Year'] >= int(start_season)) &
            (self.data['Season Year'] <= int(end_season))
        ]

        # Filter for league averages in the selected seasons
    #    league_avg_data = self.data[
    #       (self.data['Name'] == f"Season {selected_season} Average")
    #    ]

        if filtered_player_data.empty:
            self.player_stats_table.clear()
            self.player_stats_table.setRowCount(0)
            self.player_stats_table.setColumnCount(0)
            self.player_stats_table.setHorizontalHeaderLabels(['No Data Available'])
            return
        
        agg_data = filtered_player_data.sum(numeric_only = True)

        stats = [
            (STAT_MAPPING.get(col, col), agg_data[col])
            for col in agg_data.index
            if col in STAT_MAPPING
        ]

        self.player_stats_table.clear()
        self.player_stats_table.setRowCount(len(stats))
        self.player_stats_table.setColumnCount(2)  # Columns: Stat, Player Value
        self.player_stats_table.setHorizontalHeaderLabels(["Statistic", "Value"])

        for row, (stat_name, value) in enumerate(stats):
            self.player_stats_table.setItem(row, 0, QTableWidgetItem(stat_name))  # Statistic
            self.player_stats_table.setItem(row, 1, QTableWidgetItem(f'{value:.2f}' if isinstance(value, float) else str(value)))

        self.player_stats_table.resizeColumnsToContents()
        self.player_stats_table.resizeRowsToContents()
        self.player_stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.player_stats_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Update diverging bar chart for player vs. league average
        #self.update_player_chart(stats_data)

    def update_player_chart(self, stats_data: pd.DataFrame) -> None:
        try:
            self.figure_player.clear()
            self.figure_player.set_size_inches(10, len(stats_data) * 0.5)
            axes = self.figure_player.subplots(len(stats_data), 1, squeeze=False)

            for i, (stat_name, player_value, league_value) in enumerate(stats_data):
                ax = axes[i, 0]
                # Draw diverging bars for league average on the left and player stat on the right
                ax.barh([0], [league_value], color='green' if league_value > player_value else 'red', height=0.3, label="League Avg")
                ax.barh([0], [-player_value], color='green' if player_value > league_value else 'red', height=0.3, label="Player Stat")

                # Set labels and limits for better alignment
                ax.set_title(stat_name, fontsize=12, pad=20)
                ax.set_yticks([])
                ax.set_xticks([])
                ax.set_xlim(left=-max(player_value, league_value) * 1.2, right=max(player_value, league_value) * 1.2)
                ax.text(-player_value, 0, f'{player_value:.2f}', va='center', ha='left', fontsize=10, color='black')
                ax.text(league_value, 0, f'{league_value:.2f}', va='center', ha='right', fontsize=10, color='black')

                # Hide spines to make the bars stand out more
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['left'].set_visible(False)
                ax.spines['bottom'].set_visible(False)

            self.figure_player.tight_layout()
            self.canvas_player.draw()

        except Exception as e:
            print(f"Error in update_player_chart: {e}")


    def create_compare_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout()

        # Team dropdowns for P1 and P2
        self.team1_dropdown = QComboBox()
        self.team1_dropdown.addItems(['All Teams'] + [TEAM_NAME_MAPPING.get(team, team) for team in sorted(self.data['Team'].unique())])
        self.team1_dropdown.currentTextChanged.connect(self.update_player1_dropdown)

        self.team2_dropdown = QComboBox()
        self.team2_dropdown.addItems(['All Teams'] + [TEAM_NAME_MAPPING.get(team, team) for team in sorted(self.data['Team'].unique())])
        self.team2_dropdown.currentTextChanged.connect(self.update_player2_dropdown)

        # Player dropdowns for P1 and P2
        self.player1_dropdown = QComboBox()
        self.update_player1_dropdown('All Teams')
        self.player1_dropdown.currentTextChanged.connect(self.update_bar_graph)

        self.player2_dropdown = QComboBox()
        self.update_player2_dropdown('All Teams')
        self.player2_dropdown.currentTextChanged.connect(self.update_bar_graph)

        # Initialize Matplotlib figure and canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(tab)  # Explicitly set the parent to ensure proper embedding

        # Add widgets to the layout
        layout.addWidget(QLabel('Team 1:'))
        layout.addWidget(self.team1_dropdown)
        layout.addWidget(QLabel('Player 1:'))
        layout.addWidget(self.player1_dropdown)

        layout.addWidget(QLabel('Team 2:'))
        layout.addWidget(self.team2_dropdown)
        layout.addWidget(QLabel('Player 2:'))
        layout.addWidget(self.player2_dropdown)

        # Add Matplotlib canvas
        layout.addWidget(self.canvas)

        tab.setLayout(layout)
        return tab
    
    def update_player1_dropdown(self, team_name: str) -> None:
        '''
        
        Updates the dropdown menu for Player 1 based on the selected team
        
        '''
        if team_name == 'All Teams':
            filtered_data = self.data
        else:
            team_abbr = {v: k for k, v in TEAM_NAME_MAPPING.items()}.get(team_name, team_name)
            filtered_data = self.data[self.data['Team'] == team_abbr]
        self.player1_dropdown.clear()
        self.player1_dropdown.addItems(filtered_data['Name'].unique())

    def update_player2_dropdown(self, team_name: str) -> None:
        '''
        
        Updates the dropdown menu for Player 2 based on the selected team

        '''
        if team_name == 'All Teams':
            filtered_data = self.data
        else:
            team_abbr = {v: k for k, v in TEAM_NAME_MAPPING.items()}.get(team_name, team_name)
            filtered_data = self.data[self.data['Team'] == team_abbr]
        self.player2_dropdown.clear()
        self.player2_dropdown.addItems(filtered_data['Name'].unique())

    def update_comparison_table(self) -> None:
        '''
        
        Updates the displayed information in the comparison table based on the selected players

        '''
        player1 = self.player1_dropdown.currentText()
        player2 = self.player2_dropdown.currentText()

        player1_data = self.data[self.data['Name'] == player1]
        player2_data = self.data[self.data['Name'] == player2]
        
        self.display_comparison(player1_data, player2_data)

    def display_comparison(self, player1_data: pd.DataFrame, player2_data: pd.DataFrame) -> None:
        '''
        
        Helper function for above
        
        '''
        if player1_data.empty or player2_data.empty:
            self.comparison_table.clear()
            self.comparison_table.setRowCount(0)
            self.comparison_table.setColumnCount(0)
            self.comparison_table.setHorizontalHeaderLabels([])
            return
        
        stats_columns = ['G', 'PA', 'HR', 'R'] #Need to fill this in with names for stats in data
        player1_stats = player1_data.iloc[0][stats_columns]
        player2_stats = player2_data.iloc[0][stats_columns]

        self.comparison_table.clear()
        self.comparison_table.setRowCount(len(stats_columns))
        self.comparison_table.setColumnCount(3) #3 cols for stat name, player 1, and player 2
        self.comparison_table.setHorizontalHeaderLabels(['Statistic', 'Player 1', 'Player 2'])

        for row, stat in enumerate(stats_columns):
            self.comparison_table.setItem(row, 0, QTableWidgetItem(stat)) #Statistic name
            self.comparison_table.setItem(row, 1, QTableWidgetItem(str(player1_stats[stat])))
            self.comparison_table.setItem(row, 2, QTableWidgetItem(str(player2_stats[stat])))
        
        self.comparison_table.resizeColumnsToContents()
        self.comparison_table.resizeRowsToContents()


    def update_bar_graph(self) -> None:
        '''
        
        Updates the various visualizations present in the compare tab based on selected values
        
        
        '''
        try:
            # Get selected players
            player1_name = self.player1_dropdown.currentText()
            player2_name = self.player2_dropdown.currentText()

            # Fetch player data
            player1_data = self.data[self.data["Name"] == player1_name]
            player2_data = self.data[self.data["Name"] == player2_name]

            if player1_data.empty or player2_data.empty:
                print(f"Error: Data missing for {player1_name} or {player2_name}.")
                return

            # Stat groups
            power_stats = ["HR", "R", "RBI", "SB"]
            high_range_stats = ["PA"]
            advanced_stats = ["WAR", "Def"]
            percentage_stats = ["BB%", "K%"]

            # Extract data for each group
            player1_power = player1_data[power_stats].iloc[0].fillna(0).astype(float)
            player2_power = player2_data[power_stats].iloc[0].fillna(0).astype(float)

            player1_high_range = player1_data[high_range_stats].iloc[0].fillna(0).astype(float)
            player2_high_range = player2_data[high_range_stats].iloc[0].fillna(0).astype(float)

            player1_advanced = player1_data[advanced_stats].iloc[0].fillna(0).astype(float)
            player2_advanced = player2_data[advanced_stats].iloc[0].fillna(0).astype(float)

            player1_percentage = player1_data[percentage_stats].iloc[0].fillna(0).astype(float)
            player2_percentage = player2_data[percentage_stats].iloc[0].fillna(0).astype(float)

            # Clear the figure
            self.figure.clear()

            # Set figure size
            self.figure.set_size_inches(12, 10)

            # Create subplots
            axes = self.figure.subplots(2, 2)

            # Plot power stats
            x = range(len(power_stats))
            axes[0, 0].bar(x, player1_power, width=0.4, label=player1_name, color='blue')
            axes[0, 0].bar([i + 0.4 for i in x], player2_power, width=0.4, label=player2_name, color='orange')
            axes[0, 0].set_title("Power Stats")
            axes[0, 0].set_xticks([i + 0.2 for i in x])
            axes[0, 0].set_xticklabels(power_stats, rotation=30, ha='right')

            # Plot high-range stats
            x = range(len(high_range_stats))
            axes[0, 1].bar(x, player1_high_range, width=0.4, label=player1_name, color='blue')
            axes[0, 1].bar([i + 0.4 for i in x], player2_high_range, width=0.4, label=player2_name, color='orange')
            axes[0, 1].set_title("High-Range Stats")
            axes[0, 1].set_xticks([i + 0.2 for i in x])
            axes[0, 1].set_xticklabels(high_range_stats, rotation=30, ha='right')

            # Plot advanced stats
            x = range(len(advanced_stats))
            axes[1, 0].bar(x, player1_advanced, width=0.4, label=player1_name, color='blue')
            axes[1, 0].bar([i + 0.4 for i in x], player2_advanced, width=0.4, label=player2_name, color='orange')
            axes[1, 0].set_title("Advanced Stats")
            axes[1, 0].set_xticks([i + 0.2 for i in x])
            axes[1, 0].set_xticklabels(advanced_stats, rotation=30, ha='right')

            # Plot percentage stats
            x = range(len(percentage_stats))
            axes[1, 1].bar(x, player1_percentage, width=0.4, label=player1_name, color='blue')
            axes[1, 1].bar([i + 0.4 for i in x], player2_percentage, width=0.4, label=player2_name, color='orange')
            axes[1, 1].set_title("Percentage Stats")
            axes[1, 1].set_xticks([i + 0.2 for i in x])
            axes[1, 1].set_xticklabels(percentage_stats, rotation=30, ha='right')

            # Add a single legend for the entire figure
            handles, labels = axes[0, 0].get_legend_handles_labels()
            self.figure.legend(handles, labels, loc='upper right', fontsize=10)

            # Adjust layout
            self.figure.subplots_adjust(hspace=0.5, wspace=0.4)

            # Refresh canvas
            self.canvas.draw()

        except Exception as e:
            print(f"Error in update_bar_graph: {e}")
