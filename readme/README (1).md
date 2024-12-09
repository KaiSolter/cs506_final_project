**Lichess Blitz Prediction Model Midterm Report**  
By: Tia Zheng, Rebecca Geisberg, Kai Solter  
**YOUTUBE LINK: [https://youtu.be/ltHeIY71sFI](https://youtu.be/ltHeIY71sFI)**

1. **Introduction**

   

   Over the years, AI has become a powerful tool across industries, transforming fields from financial analysis to medical breakthroughs. While much of AI's power has gone toward serious advancements, we decided to explore a lighter application: predicting outcomes in Lichess Blitz chess games using machine learning. This technology enables computers to identify complex patterns in data and make informed predictions—perfect for analyzing the intricate dynamics of chess.

   

   In chess, player ratings—a numerical score reflecting skill based on past wins and losses—typically make game outcomes easy to predict, especially when there’s a large rating gap. However, we wanted to see if a model could reveal more subtle factors that might affect the result, such as the color of the pieces each player controls, recent performance trends, and etc. Our goal is to uncover scenarios where a lower-rated player might triumph over a higher-rated opponent, or determine the outcome in matches between similarly rated competitors.

   

   By analyzing these nuances, we hope to add a new layer of insight into chess outcomes in online play, looking beyond basic ratings to understand the deeper dynamics of competitive Blitz chess.

   

   

2. **Data Collection**

   Our current data sample contains a small preliminary set of users from distinct lichess 

   rating sub-brackets, overall ranging from around 550 to 2750, as the minimum rating on the platform is 400 and the max is 2900\. To build this dataset, we manually pick users that fall in the median of each 150-point rating sub-bracket, a choice driven by our data collection method. Specifically, our approach involves repeatedly retrieving each user’s past 15 opponents recursively, adding these players to the user\_id list. We continued until reaching a list of approximately 4000 unique user\_ids. Once we established this user base, we looped through the list of user\_ids to obtain each user's Blitz rating from the Lichess API. Focusing on Blitz-style gameplay, we used this list to retrieve additional game-related features from each user's recent Blitz games. 

   These features include:

   

1. **Blitz Rating** (blitz\_rating): The user’s current rating in Blitz.  
2. **Total Games Played** (total\_games\_played): The all-time number of Blitz games played by the user on Lichess.  
3. **Game Count** (game\_count): The number of Blitz games each user had played within their most recent 300 games, capped at 100 Blitz games per user. For users with fewer than 100 Blitz games (out of the recent 300), win, draw, and loss rates are calculated based on the total games available. To ensure data accuracy in reflecting current skill and activity, we excluded users who hadn’t played any Blitz games within their last 300 games.  
4. **Top Opponents Defeated** (highest\_blitz\_opponent\_rating, second\_highest\_blitz\_opponent\_rating, third\_highest\_blitz\_opponent\_rating): The ratings of the highest, second-highest, and third-highest rated opponents the user has defeated.  
5. **Win/Loss Streaks** (win\_streak\_current, win\_streak\_max, loss\_streak\_current, loss\_streak\_max, total\_games\_played): Number of consecutive wins or losses for a user  
6. **Rating Deviation** (rating\_deviation): Measures how accurately a user’s rating reflects their current skill level. Lower value means the rating is more stable. Above 110, the rating is considered provisional. To be included in the rankings, this value should be below 75 (standard chess).  
7. **Win, Draw, and Loss Rates –Based on total Game Count** (win\_rate, draw\_rate, lose\_rate): Rates that reflect the user’s overall performance across their recent Blitz games, using the total number of Blitz games retrieved (up to a maximum of 100\) from most recent 300 games as a basis. This gives a general view of the user's success, independent of color.  
8. **Win, Draw, and Loss Rates –Based on color played from total Game Count** (black\_win\_rate,black\_lose\_rate,black\_draw\_rate): Rates further broken down based on the color of pieces the user played (white or black) within the same recent Blitz games. This provides insights into any potential differences in performance when playing as white versus black.  
   

   It should be noted that our data has the above features for both the user and their opponent. *Specifically*, the csv used by the models contains the user id and the above features for the user, and then the opponent id and the features for the opponent, then finally the result of their head to head match.

	

3. **Preliminary Analysis and Feature Engineering**

**SEE IPYNB FOR GRAPHS/VISUALIZATION OF DATA 


**Data Preparation**

The first step in our preprocessing is to remove or convert non categorical variables into numerical ones. As of right now that simply involves dropping the names of the users, although we may later experiment with one-hot encoding.  
Next we removed irrelevant users based on our preliminary analysis. We decided to remove users that had played less than a total of 10 games, in order to ensure that the features were relevant to the user.  Additionally, we removed users with zero games as white, or zero games as black. If one of the scripts we made that uses the API to fetch data fails, it will zero out only the color specific features. However, there is a different script that fetched the total games of the user, and therefore we needed to make sure that both API calls were successful to ensure the accuracy of our dataset. There could theoretically be a user with a total game count above 10, but zeroed out color specific features, and this methodology prevents that user from skewing the predictions. Finally we also removed users which had NaN in any feature as they simply represent an error with the api.


**SEE IPYNB FOR CORRELATION MATRIX
	

We decided to drop irrelevant features, and the features that we were left with are:

'user\_black\_game\_count', 'user\_black\_draw\_rate', 'user\_black\_win\_rate', 'user\_blitz\_rating', 'user\_draw\_rate', 'user\_game\_count', 'user\_highest\_blitz\_opponent\_rating',  'user\_win\_rate', 'user\_rating\_deviation', 'user\_total\_games\_played', 'user\_white\_draw\_rate', 'user\_white\_game\_count', 'user\_white\_win\_rate'. 

As well as the corresponding opponent features.

We decided to include the win and draw rate as well as the color specific win and draw rates, but drop loss rates because the information of the loss rate is sufficiently conveyed by the win and draw rate as the only possible outcomes and win, loss and draw. We decided to remove all the win/loss streak data pending further analysis as we were worried that it could potentially directly spoil the outcome of the game. We furthermore dropped the second and third best win, as we felt that information is sufficiently conveyed by the highest win alone.

4. **Model Selection**  
   Our model will be predicting a categorical outcome, as the results of a chess game can only be a win, a loss, or a draw. We first start out by using the basic KNN model, because it is good at predicting categorical outcomes. We also decided to use RandomForest because it can ideally pick up more complex relationships.  
     
   In order to tune our hyperparameters to obtain our best performing model, we used grid search. The grid search uses 5-fold cross validation, and calculates the average accuracy to obtain the best parameters.   
     
   KNN Result: 0.5198098256735341  
   KNN Best Parameters: {'n\_neighbors': 50, 'weights': 'distance'}  
   RandomForest Result: 0.6101426307448494

	RandomForest Best Parameters: {'max\_depth': 20, 'n\_estimators': 100}

5. **Reflection**  
   Upon reflection, we are going to get more and better features. For example, we could add a feature for opening analysis, where we would get the x most popular openings for both user and op. Another feature we could include is the performance by opening for user and op, similar to how we conducted statistics based on the color of the piece.  Additionally, we can include which color each player was playing, as well as dropping features that aren't proving useful. Not only this, but we can derive new features from our preexisting ones. For example, we could include a new feature that contains the difference between white and black win rate.  
     
   Not only will we try and include new features, but we will also most likely use neural networks to see how that performs against our manual feature selection. Additionally, while we are currently using KNN and RandomForest, we will also try XGBoost, and possibly some other models in order to make sure that we are choosing the best model.   
     
   When we were collecting our data, the main issue we ran into was rate limiting with the Lichess API. When we were trying to get our initial user id list, we were requesting data too fast, which was really halting our progress. However, we ended up changing our code so that when we run into rate limiting issues, we save our progress into a csv, and pick up from where we left off. Even with this system in place, the rate limiting was a significant challenge in terms of timely data collection.   
 


6. **Sources**

   **Lichess.org.** *Lichess API Documentation*. Lichess.org, https://lichess.org/api. Accessed 5 Nov. 2024\.

   

![Screenshot](images/070B7FBB-6D67-4687-8733-9A5B12B0DE5B_1_105_c.jpeg)

