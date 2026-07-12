# FIFA World Cup 2026 Semi-Final Predictor 🏆

A quick Monte Carlo simulation to predict the FIFA World Cup 2026 semi-finals, France vs Spain and England vs Argentina. Runs each match 10,000 times using a Poisson goal model built from each team's tournament form (goals scored/conceded per game).

## How it works

- Every team gets an **Attack Strength** and **Defence Weakness** score based on their goals-for and goals-against per game so far in the tournament.
- Expected goals for each match are calculated by combining one team's attack with the other's defence.
- Each match is simulated 10,000 times using a Poisson distribution for goals.
- If a simulation ends in a draw, the winner is decided by a penalty shootout — weighted slightly toward the team with the better attack-to-defence balance.
- The team that wins the most simulations is the predicted winner.

## Running it

Run the script with:

python semis_simulation.py

This will:
- Print a results table for both semi-finals
- Print the predicted winner of each match
- Save two CSVs (simulation results + team form stats)
- Save a bar chart comparing win probabilities

## Files generated

- `semis_10000_updated_webdata_results.csv` — full simulation results
- `semis_10000_updated_webdata_team_form.csv` — attack/defence numbers per team
- `semis_10000_updated_webdata_plot.png` — win probability chart

## Notes

Team stats (goals for/against, matches played) are plugged in manually update the `teams` dictionary with the latest numbers before running if the tournament has moved on. This is just a fun statistical model, not a betting tool.

Changing seed changes the output so you can play with that too 

## Thanks for having a look ❤︎