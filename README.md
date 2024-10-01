Project Proposal:


Goal: 
Predict the outcome of a chess game between two players who have never played against each other based on their performance in other games. The players' “elo” rank must be within 200 of each other, to avoid large rating gaps which make the outcome of the game obvious. In addition, we will be focused on the “blitz” time control. In order to predict who will win the game, we will use data from some of the following factors: 
Previous games and their respective outcomes
Win rate with/against different openings
Win rate with color
Time usage patterns (Game duration)
Accuracy in comparison with the engine (stockfish) 
Blunder rates
Centipawn loss
ELO Rating
Frequency of Opening opponent has played

Data Collection: 
We will use the free lichess api (https://lichess.org/api) in order to pull user’s game data. 

Visualization: 
At this stage we aren't entirely sure how we want to visualize our data some options that we are considering are: 
Barplot
Histogram
Scatterplot
Heatmap

We might use some of the below packages:

(from sklearn.metrics import confusion_matrix 
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc –visualize model’s performance)

Test Plan:
Data Collected
70% training data
20% validation data
10% test data

In general, we will take two users within the specified ELO range who have played a game against each other, and attempt to predict the game result based on their other data. We will withhold some of the sets of users for validation and testing purposes.

Modeling:
We are still making up our minds between these two modeling approaches and would appreciate feedback on which you think better supports our goals:

XGBoost: An advanced gradient-boosting method that often performs better than random forests in structured data scenarios like this. It can capture complex interactions between features.

Neural Networks (Deep Learning): consists of interconnected layers of nodes , where each node processes inputs using weights and biases, and applies an activation function to produce an output. These networks learn patterns from data through a process called backpropagation, adjusting weights to minimize error in predictions. Neural networks are widely used in tasks like image recognition, natural language processing, and other complex problem-solving areas due to their ability to model non-linear relationships in data.
